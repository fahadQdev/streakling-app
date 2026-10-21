/*
 * Streakling runtime
 * Renders the app's HTML template ({{holes}}, <sc-if>, <sc-for>) with Preact
 * and runs the app logic class (`class Component extends DCLogic`).
 * Original code for this project. Preact is MIT-licensed (see vendor/).
 */
(function () {
  'use strict';
  var h = preact.h;
  var Fragment = preact.Fragment;

  // ---------- {{ hole }} lookup ----------
  // Supports dotted paths, $index, literals and simple ===/!== comparisons.
  function lookup(scope, expr) {
    var e = String(expr).trim();
    if (!e) return undefined;
    if (e[0] === '(' && e[e.length - 1] === ')') return lookup(scope, e.slice(1, -1));
    var ops = ['!==', '===', '!=', '=='];
    for (var i = 0; i < ops.length; i++) {
      var at = e.indexOf(ops[i]);
      if (at > 0) {
        var a = lookup(scope, e.slice(0, at));
        var b = lookup(scope, e.slice(at + ops[i].length));
        switch (ops[i]) {
          case '===': return a === b;
          case '!==': return a !== b;
          case '==': return a == b; // eslint-disable-line eqeqeq
          default: return a != b; // eslint-disable-line eqeqeq
        }
      }
    }
    if (e === 'true') return true;
    if (e === 'false') return false;
    if (e === 'null') return null;
    if (e === 'undefined') return undefined;
    if (/^-?\d+(\.\d+)?$/.test(e)) return Number(e);
    if ((e[0] === '"' && e[e.length - 1] === '"') || (e[0] === "'" && e[e.length - 1] === "'")) return e.slice(1, -1);
    var parts = e.split('.');
    var v = scope;
    for (var j = 0; j < parts.length; j++) {
      if (v == null) return undefined;
      v = v[parts[j].trim()];
    }
    return v;
  }

  var HOLE = /\{\{([\s\S]+?)\}\}/g;
  // One hole and nothing else ("{{a}} {{b}}" is two holes, not one).
  var WHOLE = /^\s*\{\{((?:(?!\}\})[\s\S])+)\}\}\s*$/;

  function toText(v) {
    if (v == null || typeof v === 'boolean') return '';
    return String(v);
  }

  // Compile an attribute/text value into a function of scope.
  function compileValue(src) {
    var m = src.match(WHOLE);
    if (m) {
      var expr = m[1];
      return function (s) { return lookup(s, expr); };
    }
    if (src.indexOf('{{') !== -1) {
      var pieces = src.split(HOLE);
      return function (s) {
        var out = '';
        for (var i = 0; i < pieces.length; i++) out += (i & 1) ? toText(lookup(s, pieces[i])) : pieces[i];
        return out;
      };
    }
    return function () { return src; };
  }

  var BOOLEAN = { disabled: 1, checked: 1, readonly: 1, required: 1, selected: 1, multiple: 1, hidden: 1, autofocus: 1, open: 1, novalidate: 1 };

  function eventName(attr, tag, type) {
    var rest = attr.slice(2).toLowerCase();
    if (rest === 'change') {
      // React semantics: onChange on text fields fires on every keystroke.
      if (tag === 'textarea') return 'onInput';
      if (tag === 'input' && !/^(checkbox|radio|file|range|color)$/i.test(type || '')) return 'onInput';
      return 'onChange';
    }
    return 'on' + rest;
  }

  // ---------- compile DOM nodes into render functions ----------
  function compileChildren(node) {
    var out = [];
    for (var c = node.firstChild; c; c = c.nextSibling) {
      var f = compileNode(c);
      if (f) out.push(f);
    }
    return out;
  }

  function renderList(fns, scope) {
    var out = [];
    for (var i = 0; i < fns.length; i++) out.push(fns[i](scope, i));
    return out;
  }

  function compileNode(node) {
    if (node.nodeType === 3) {
      var text = node.nodeValue || '';
      if (text.indexOf('{{') === -1) {
        // Whitespace-only runs without a plain space are layout noise.
        if (!text.trim() && text.indexOf(' ') === -1) return null;
        return function () { return text; };
      }
      // Keep the literal text around holes, including spaces.
      var pieces = text.split(HOLE);
      return function (s) {
        var out = '';
        for (var i = 0; i < pieces.length; i++) out += (i & 1) ? toText(lookup(s, pieces[i])) : pieces[i];
        return out;
      };
    }
    if (node.nodeType !== 1) return null;
    var tag = node.localName;

    if (tag === 'sc-if') {
      var cond = compileValue(node.getAttribute('value') || '');
      var kids = compileChildren(node);
      return function (s, k) {
        return cond(s) ? h(Fragment, { key: k }, renderList(kids, s)) : null;
      };
    }

    if (tag === 'sc-for') {
      var list = compileValue(node.getAttribute('list') || '');
      var as = node.getAttribute('as') || 'item';
      var body = compileChildren(node);
      return function (s, k) {
        var arr = list(s);
        if (!Array.isArray(arr)) arr = [];
        return h(Fragment, { key: k }, arr.map(function (item, idx) {
          var inner = Object.assign({}, s);
          inner[as] = item;
          inner.$index = idx;
          return h(Fragment, { key: idx }, renderList(body, inner));
        }));
      };
    }

    var type = node.getAttribute('type') || '';
    var attrs = [];
    for (var i = 0; i < node.attributes.length; i++) {
      var a = node.attributes[i];
      var name = a.name;
      if (name.indexOf('hint-') === 0) continue;
      var lower = name.toLowerCase();
      var val = compileValue(a.value);
      if (lower.indexOf('on') === 0 && lower.length > 2) {
        attrs.push({ name: eventName(name, tag, type), val: val, event: true });
      } else if (lower === 'ref') {
        attrs.push({ name: 'ref', val: val });
      } else if (BOOLEAN[lower] && a.value === '') {
        attrs.push({ name: lower, val: function () { return true; } });
      } else {
        attrs.push({ name: name, val: val });
      }
    }
    var children = compileChildren(tag === 'template' ? node.content : node);

    return function (s, k) {
      var props = { key: k };
      for (var j = 0; j < attrs.length; j++) {
        var at = attrs[j];
        var v = at.val(s);
        if (at.event) { if (typeof v === 'function') props[at.name] = v; continue; }
        if (v === undefined) continue;
        props[at.name] = v;
      }
      return h(tag, props, renderList(children, s));
    };
  }

  // ---------- logic base class ----------
  function DCLogic(props) { preact.Component.call(this, props); }
  DCLogic.prototype = Object.create(preact.Component.prototype);
  DCLogic.prototype.constructor = DCLogic;
  DCLogic.prototype.render = function () {
    var vals = typeof this.renderVals === 'function' ? this.renderVals() : {};
    return h(Fragment, null, renderList(DCLogic._root, vals || {}));
  };
  window.DCLogic = DCLogic;

  // ---------- boot ----------
  function showError(err) {
    var box = document.getElementById('boot-error');
    if (!box) return;
    box.hidden = false;
    box.textContent = 'Something went wrong while loading the app.\n\n' + (err && err.stack ? err.stack : String(err));
  }

  window.addEventListener('error', function (e) { showError(e.error || e.message); });

  window.StreaklingBoot = function (opts) {
    try {
      var tpl = document.getElementById(opts.template);
      DCLogic._root = compileChildren(tpl.content);
      var Comp = opts.component();
      preact.render(h(Comp, opts.props || {}), document.getElementById(opts.mount));
    } catch (err) {
      showError(err);
      throw err;
    }
  };
})();
