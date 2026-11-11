/*
 * carousel-kit.js —  carousel renderer (block-text set).
 *
 * LOCKED 2026-10-09 by the user, modeled on Jess Pinili's slides:
 * every slide is ONE tight block of Helvetica Neue — no paragraph gaps,
 * lines running the full width so the block reads as a solid rectangle, sized per slide so
 * the block fills the width, sitting in the middle of the slide.
 *
 * TWO themes, one per carousel: 'dark' (black bg, white text) or 'light'.
 * TWO alignments, one per carousel: 'center' (default) or 'left'.
 *
 * Copy markup inside `text` (body is Helvetica Neue Bold):
 *   {light words}   → Light weight            "content {that never} ceases"
 *   _italic words_  → italic (keeps weight)   "but _now_, it's not enough"
 *   {_both_}        → light italic            "The question {_isn't_} whether"
 *   ~~text~~        → strikethrough
 *   keyword: 'X'    → X bold + underlined (CTA slides)
 *
 * Sizing: by default the fit script picks the largest size (MIN..MAX) where
 * the block fits the box (900px wide, MAX_H tall). Like Canva, any slide can
 * be adjusted by eye: `size: 90` fixes the font size, `width: 760` narrows
 * the box (still centered). Use judgment, look at the render, nudge.
 *
 * Build:  CarouselKit.buildCarouselHTML(slides, { theme, align })
 */
(function (root) {
  'use strict';

  var BLACK = '#000000';
  var WHITE = '#FFFFFF';
  var FONT = '\'Helvetica Neue\', Helvetica, Arial, sans-serif';
  var LEADING = 0.82;
  var TRACKING = '-0.065em';
  var MARGIN = 90;        // px each side → 900px box
  var MAX_H = 720;        // px, tallest the block may get (~53% of the slide)
  var MIN = 60, MAX = 100; // px font-size range for the fit

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function fmt(text) {
    return esc(text)
      .replace(/~~([\s\S]+?)~~/g, '<s>$1</s>')
      .replace(/\*\*([\s\S]+?)\*\*/g, '<strong style="font-weight:700;opacity:1;">$1</strong>')
      .replace(/\[\[([\s\S]+?)\]\]/g, '<span class="ck-acc" style="color:var(--accent,#fff);">$1</span>')
      .replace(/\{([\s\S]+?)\}/g, '<span style="font-weight:300;letter-spacing:-0.045em;">$1</span>')
      .replace(/(^|[\s(“"'{>])_([^_]+?)_(?=$|[\s.,!?;:)”"'’<}])/g, '$1<em style="font-style:italic;padding-right:.04em;">$2</em>')
      .replace(/\n/g, '<br>');
  }

  function theme(name) {
    var dark = name !== 'light';
    return { bg: dark ? BLACK : WHITE, ink: dark ? WHITE : BLACK };
  }

  function sectionOpen(label, idx, notes) {
    return '<section data-label="' + esc(label) + '" data-screen-label="' + String(idx + 1).padStart(2, '0')
      + '" data-speaker-notes="' + esc(notes || '') + '" style="width:100%;height:100%;">';
  }

  var LAYOUTS = {
    text: function (d, ctx) {
      var t = ctx.theme;
      // `text` is the slide's one block. `lines` (old format) is joined into one block.
      var src = d.text != null ? d.text : (d.lines || []).join(' ');
      var h = fmt(src);
      var kws = d.keyword ? (Array.isArray(d.keyword) ? d.keyword : [d.keyword]) : [];
      kws.forEach(function (kw) {
        h = h.split(esc(kw)).join('<span style="font-weight:700;text-decoration:underline;text-decoration-thickness:.07em;text-underline-offset:.1em;">' + esc(kw) + '</span>');
      });
      var w = d.width || (1080 - 2 * MARGIN);
      return sectionOpen('Text', ctx.idx, d.notes)
        + '<div style="position:relative;width:100%;height:100%;background:' + t.bg + ';color:' + t.ink + ';font-family:' + FONT + ';overflow:hidden;">'
        + '<div class="ck-block"' + (d.size ? ' data-size="' + d.size + '"' : '') + ' style="position:absolute;width:' + w + 'px;left:50%;top:50%;transform:translate(-50%,-50%);'
        + 'font-size:' + (d.size || MAX) + 'px;line-height:' + LEADING + ';font-weight:700;letter-spacing:' + TRACKING + ';text-align:' + ctx.align + ';text-wrap:pretty;">'
        + h + '</div></div></section>';
    }
  };

  /*
   * PHOTO layout (added 2026-10-12, modeled on Jess Pinili carousels 1/4/5):
   * graded photo behind the slide (run assets/grade.py first — never use an ungraded photo),
   * bold headline + lighter body, small footer "" / "swipe left".
   *   { layout:'photo', bg:'bg.jpg', label:'#1:', headline:'...', body:['para with **key phrase**'], kicker:'punchline', cta:'...', keyword:'X' }
   * Hierarchy (Jess-style): small label above the headline, **bold** key phrases in body,
   * kicker = the payoff line in bold, cta = boxed. `quote:true` = smaller italic quote in “ ”,
   * always centered both ways (the user, 2026-10-12).
   * Headline and body auto-fit together; `size` fixes the headline size by eye.
   *
   * SIZE = IMPORTANCE (the user, 2026-10-13). Every slide gets a role; the role sets the size range
   * (see ROLES in FIT). cover + cta = biggest (the two slides that sell). body = a clear step down.
   * solo (one line, no body) = mid-size and tasteful, never cover-size (big text on an emotional
   * line reads childish). quote = smallest. Body text, labels and `sub` scale off the headline.
   * Every block is vertically centered; nothing sits in the lower half. Safe margins: 100px
   * left/right, ~195px top/bottom (P_W, P_MAX_H). Fit by stepping sizes down within the role's
   * range — never below its floor; if it still won't fit, fix the layout, not the size.
   * `sub` = a smaller modifying line under the headline (e.g. "(and you shouldn't either)").
   * `lead` = a lead-in line above the headline at ~80% of its size (e.g. "Gun to the head:").
   * `tail` = the end statement after the headline at ~72% (e.g. "here's what I'd do:").
   * COVER COLOR RULE (the user, 2026-10-13): the headline is all white; lead / tail / sub (the smaller
   * modifying lines) are the accent color. No [[accent]] inside a cover headline.
   * The CTA keyword is always accent color + underlined.
   */
  var P_MAX_H = 960, P_W = 880;
  var PLAIN = '#171513';   // warm near-black, same darkness as the graded cover
  var PSTYLE = 'font-weight:400;line-height:1.06;letter-spacing:-0.02em;margin-top:.5em;color:rgba(255,255,255,.92);';
  LAYOUTS.photo = function (d, ctx) {
    var kws = d.keyword ? (Array.isArray(d.keyword) ? d.keyword : [d.keyword]) : [];
    function kw(h) {
      kws.forEach(function (k) {
        h = h.split(esc(k)).join('<span style="font-weight:700;color:var(--accent,#fff);text-decoration:underline;text-decoration-thickness:.07em;text-underline-offset:.12em;">' + esc(k) + '</span>');
      });
      return h;
    }
    // Body text is ONE weight on body slides (the user, 2026-10-13): bold everywhere = nothing stands out.
    // `**bold**` in body paragraphs only renders on CTA slides; the kicker stays bold as the one payoff line.
    var oneWeight = !d.cta && !d.bg;
    var body = (d.body || []).map(function (p) { return '<p class="ck-p" style="' + PSTYLE + '">' + kw(fmt(oneWeight ? p.replace(/\*\*/g, '') : p)) + '</p>'; }).join('');
    var proof = d.proof ? '<img class="ck-proof" src="' + esc(d.proof) + '" style="display:block;margin:.9em ' + (ctx.align === 'left' ? '0' : 'auto') + ' .2em;max-width:520px;max-height:' + (d.proofH || 380) + 'px;border-radius:18px;box-shadow:0 10px 40px rgba(0,0,0,.5);">' : '';
    var kicker = d.kicker ? '<p class="ck-p" style="' + PSTYLE + 'font-weight:700;margin-top:.8em;">' + kw(fmt(d.kicker)) + '</p>' : '';
    var cta = d.cta ? '<p class="ck-p" style="margin-top:1em;"><span class="ck-cta" style="display:inline-block;text-wrap:balance;font-weight:700;font-size:1.04em;letter-spacing:-0.02em;line-height:1.1;padding:.32em .5em;background:rgba(0,0,0,.42);border-radius:10px;">' + kw(fmt(d.cta)) + '</span></p>' : '';
    var label = d.label ? '<div class="ck-l" style="font-weight:500;line-height:1.1;letter-spacing:-0.015em;margin-bottom:.3em;opacity:.92;">' + kw(fmt(d.label)) + '</div>' : '';
    var tail = d.tail ? '<div class="ck-tail" style="color:var(--accent,#fff);font-weight:700;line-height:.92;letter-spacing:-0.045em;margin-top:.14em;opacity:.95;">' + kw(fmt(d.tail)) + '</div>' : '';
    var lead = d.lead ? '<div class="ck-lead" style="color:var(--accent,#fff);font-weight:700;line-height:.92;letter-spacing:-0.045em;margin-bottom:.12em;opacity:.95;">' + kw(fmt(d.lead)) + '</div>' : '';
    var sub = d.sub ? '<div class="ck-sub" style="color:var(--accent,#fff);font-weight:500;line-height:1.05;letter-spacing:-0.02em;margin-top:.35em;opacity:.92;">' + kw(fmt(d.sub)) + '</div>' : '';
    var role = d.quote ? 'quote' : d.bg ? 'cover' : d.cta ? 'cta' : (d.headlineOnly || !(d.body || d.proof || d.label || d.kicker)) ? 'solo' : 'body';
    var foot = 'position:absolute;bottom:58px;font-size:26px;letter-spacing:-0.01em;opacity:.8;';
    return sectionOpen('Photo', ctx.idx, d.notes)
      // photo on the COVER only (graded by grade.py); every other slide is flat PLAIN (the user, 2026-10-12)
      + '<div style="position:relative;width:100%;height:100%;background:' + (d.textOnly ? 'transparent' : d.bg || ctx.backdrop ? '#000 url(\'' + esc(d.bg || ctx.backdrop) + '\') center/cover no-repeat' : (ctx.plain || PLAIN)) + ';--accent:' + (ctx.accent || '#fff') + ';color:#fff;font-family:' + FONT + ';overflow:hidden;">'
      + '<div class="ck-photo" data-role="' + role + '"' + (d.size ? ' data-size="' + d.size + '"' : '')
      + ' data-maxh="' + (d.maxH || ctx.maxH || P_MAX_H) + '"'
      + ' style="position:absolute;width:' + (d.width || (d.quote ? ctx.quoteW : ctx.width) || P_W) + 'px;'
      + (ctx.width && !d.quote ? 'left:90px;' : 'left:50%;')
      + (d.top ? 'top:' + d.top + 'px;' + (ctx.width ? '' : 'transform:translateX(-50%);')
        : d.bottom ? 'bottom:' + d.bottom + 'px;' + (ctx.width ? '' : 'transform:translateX(-50%);')
        : ctx.bottom
          ? (d.quote ? 'top:' + (1350 - ctx.bottom - (ctx.maxH || P_MAX_H) / 2) + 'px;transform:translate(-50%,-50%);'
                     : 'bottom:' + ctx.bottom + 'px;' + (ctx.width ? '' : 'transform:translateX(-50%);'))
          : (ctx.top && !d.quote ? 'top:' + ctx.top + 'px;' + (ctx.width ? '' : 'transform:translateX(-50%);') : 'top:50%;transform:translate(calc(-50% + ' + (d.shiftX || 0) + 'px),calc(-50% + ' + (d.shiftY || 0) + 'px)) scale(' + (d.scale || 1) + ');'))
      + 'text-align:' + (d.quote ? 'center' : (d.align || ctx.align)) + ';text-wrap:' + (d.quote || d.bottom || d.bg ? 'balance' : 'pretty') + ';text-shadow:0 2px 14px rgba(0,0,0,.35);">'
      + label
      + lead
      + (d.quote
        ? '<h1 class="ck-h" data-quote="1" style="font-weight:500;font-style:italic;line-height:1.12;letter-spacing:-0.025em;">&ldquo;' + kw(fmt(d.headline || '')) + '&rdquo;</h1>'
        : '<h1 class="ck-h" style="font-weight:700;line-height:.9;letter-spacing:-0.05em;">' + kw(fmt(d.headline || '')) + '</h1>')
      + tail
      + sub
      + (body ? '<div class="ck-b" style="margin-top:.55em;">' + body + '</div>' : '')
      + kicker + proof + cta + '</div>'
      + (d.noFoot ? '' : '<div style="' + foot + 'left:70px;font-weight:500;"></div>')
      + (d.last || d.noFoot ? '' : '<div style="' + foot + 'right:70px;font-size:40px;bottom:50px;">&rarr;</div>')
      + '</div></section>';
  };

  // Runs in the page: shrink each block from MAX until it fits, then flag done.
  var FIT = '(function(){function fit(){document.querySelectorAll(".ck-block").forEach(function(b){'
    + 'if(b.dataset.size)return;var s=' + MAX + ';b.style.fontSize=s+"px";'
    + 'while(s>' + MIN + '&&(b.scrollHeight>' + MAX_H + '||b.scrollWidth>b.clientWidth+1)){s-=1;b.style.fontSize=s+"px";}'
    + '});'
    + 'document.querySelectorAll(".ck-photo").forEach(function(b){'
    // ROLES: [headline start, headline floor, body ratio, body min, body max]
    + 'var ROLES={cover:[118,84,.45,40,56],cta:[112,80,.42,38,50],body:[90,66,.64,46,58],solo:[70,56,.6,36,44],quote:[56,40,.6,34,40]};'
    + 'var R=ROLES[b.dataset.role]||ROLES.body;var mh=+b.dataset.maxh;var s=b.dataset.size?+b.dataset.size:R[0];'
    + 'function set(s){b.querySelector(".ck-h").style.fontSize=s+"px";var bs=Math.max(R[3],Math.min(R[4],Math.round(s*R[2])));'
    + 'b.style.fontSize=bs+"px";var l=b.querySelector(".ck-l");if(l)l.style.fontSize=Math.max(30,Math.min(44,Math.round(s*0.48)))+"px";'
    + 'var u=b.querySelector(".ck-sub");if(u)u.style.fontSize=Math.max(40,Math.round(s*0.46))+"px";'
    + 'var ld=b.querySelector(".ck-lead");if(ld)ld.style.fontSize=Math.round(s*0.8)+"px";var tl=b.querySelector(".ck-tail");if(tl)tl.style.fontSize=Math.round(s*0.72)+"px";}'
    + 'set(s);if(b.dataset.size)return;'
    + 'while(s>R[1]&&(b.scrollHeight>mh||b.scrollWidth>b.clientWidth+1)){s-=2;set(s);}'
    + '});'
    + 'document.documentElement.setAttribute("data-fit","done");}'
    + 'window.addEventListener("load",function(){(document.fonts?document.fonts.ready:Promise.resolve()).then(fit);});})();';

  function buildSection(slide, ctx) {
    var fn = LAYOUTS[slide.layout || 'text'];
    if (!fn) throw new Error('Unknown layout: ' + slide.layout + ' (use: text | photo)');
    return fn(slide, ctx);
  }

  function buildCarouselHTML(slides, opts) {
    opts = opts || {};
    var ctx = { theme: theme(opts.theme), align: opts.align === 'left' ? 'left' : 'center', top: opts.top, maxH: opts.maxH, width: opts.width, quoteW: opts.quoteW, bottom: opts.bottom, backdrop: opts.backdrop, plain: opts.plain, accent: opts.accent };
    var sections = slides.map(function (s, i) {
      return buildSection(s, { idx: i, theme: ctx.theme, align: ctx.align, top: ctx.top, maxH: ctx.maxH, width: ctx.width, quoteW: ctx.quoteW, bottom: ctx.bottom, backdrop: ctx.backdrop, plain: ctx.plain, accent: ctx.accent });
    }).join('\n\n');

    return '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>Carousel</title>\n'
      + '<style>\n  *{margin:0;box-sizing:border-box;}\n  html,body{height:100%;}\n  body{background:#0c0c0a;}\n  deck-stage:not(:defined){visibility:hidden;}\n</style>\n</head>\n<body>\n\n'
      + '<deck-stage width="1080" height="1350">\n\n'
      + sections
      + '\n\n</deck-stage>\n\n'
      + '<script>' + FIT + '</script>\n'
      + '<script src="./image-slot.js"></script>\n<script src="./deck-stage.js"></script>\n</body>\n</html>\n';
  }

  root.CarouselKit = {
    LAYOUTS: LAYOUTS, fmt: fmt,
    buildSection: buildSection, buildCarouselHTML: buildCarouselHTML
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = root.CarouselKit;
})(typeof window !== 'undefined' ? window : globalThis);
