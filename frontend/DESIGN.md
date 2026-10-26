---
version: alpha
name: reel-guard-design
description: A restrained, professional dark interface modelled on Instagram web. Near-black canvas, icon-only left rail, a single blue accent for actions, the Instagram gradient reserved for unseen story rings, and one light "sponsored" card that breaks the dark rhythm on purpose.
colors:
  canvas: "#0c1014"
  surface: "#12171c"
  pill: "#262a30"
  pill-hover: "#363b42"
  hairline: "#262a30"
  ink: "#f5f5f5"
  mute: "#a8adb3"
  accent: "#4a5df9"
  link: "#7b88ff"
  like: "#ff3040"
  ring-gradient: "linear-gradient(45deg,#f9a825,#ee2a7b 55%,#8134af)"
  ad-surface: "#f4f1ea"
  ad-ink: "#101418"
  allow: "#3ecf8e"
  transform: "#e8b04a"
  redact: "#b79cff"
  block: "#ff6b78"
typography:
  family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif
  body: { size: 14px, weight: 400, lineHeight: 1.4 }
  strong: { weight: 600 }
  title: { size: 24px, weight: 700, letterSpacing: -0.3px }
  caption: { size: 12px, weight: 400 }
rounded: { media: 8px, card: 16px, button: 10px, pill: 9999px, reel: 16px }
spacing: { rail: 72px, feed-column: 470px, side-column: 320px, rail-item: 48px, icon: 24px }
---

## Principles
1. **Look like Instagram, stay quiet.** Colour is almost absent. Blue (`accent`) is the only action colour, red appears only on an active like, and the gradient appears only on unseen story rings.
2. **Dark only.** No light theme. The single light surface is the sponsored reel, used so ads read as a different object at a glance.
3. **Everything aligns to a 4px grid.** Rail items are 48px squares, icons 24–28px, feed column 470px, row heights 40/48/56px.
4. **Flat.** No shadows on content; hairlines and tonal surfaces carry depth. Only floating layers (toast, notification panel, menu) have a soft shadow.

## Layout map (from the reference screenshots)
| Area | Structure |
|---|---|
| Left rail (72px, fixed) | Logo, Home, Reels, Messages, Search, Notifications, Create, Profile avatar, then pinned to bottom: Data Privacy Analysis (with live record count badge) and More. Icon-only; label tooltip on hover. Active item is filled (home, heart, send, bookmark) or bolder stroke. |
| Home | Centered 470px column: story row (66px avatars, 3px gradient ring), then posts. Right 320px column: own account and "Suggested for you" (hidden under 1100px). |
| Post | 36px avatar, bold username, muted age, follow link, 4:5 media, action row (like, comment, share … save), likes, caption with clickable hashtags, comment count, inline comment box. Double-click the media to like. |
| Reels | Full-height snap scroller. 9:16 rounded video centred; overlay with author, Follow, caption, audio; right-hand column of like, comment, repost, share, save, more, audio tile; up/down circle buttons fixed far right; mute chip bottom-right of video. |
| Sponsored reel | Same 9:16 footprint, light `ad-surface` card, blue outline, "Sponsored" + "AD" labels, headline, perks, and a full-width blue **Apply now** button. Unmistakably a form entry point. |
| Messages | Two panels. Left: account switcher header, compose, search pill, notes row, thread list (selected row is a rounded `pill` fill). Right: header with call/video/info, bubbles, centred timestamps, rounded input with emoji, mic, image, sticker. |
| Search | Centered 640px pill field, hashtag chips, 3-column 3:4 explore grid; reels carry a white play badge; hover shows counts. |
| Notifications | 400px panel sliding out from the rail with filter pills (All, People you follow, Comments, Follows), "Today" / "This month" groups, follow-back buttons. |
| Profile | 140px avatar, username, Edit profile / View archive, stats, bio, highlights, tabs (Posts, Saved, Tagged), 3-column grid. Other users show Follow / Message. |
| Data Privacy Analysis | Same canvas and card language. Six pill tabs: flow, policy, original vs protected, third-party ads, aggregate and charts, recommendations. Action badges use tinted fills, never solid colour blocks. |
| Floating Messages pill | Bottom-right, 56px tall, `pill` fill, send icon, label and two stacked avatars. Hidden on Messages and Reels. |

## Components
- **Buttons**: primary = `accent` fill, 36px high, 10px radius; secondary = `pill` fill; text links use `link`. "Following" state is `mute`.
- **Chips**: 36px, pill radius, 1px `pill-hover` border; active = `pill` fill.
- **Avatars**: circular, muted desaturated tone derived from the handle (hsl 20% saturation) so no avatar competes with content.
- **Inputs**: `pill` fill, 12px radius, no border, 44px high.
- **Modals**: `#1b2026` surface, 16px radius, 48px header with centred title and close icon.
- **Toast**: bottom-centre, shows the Real Guard decision for each captured field.

## Do / Don't
- Do keep one accent. Do keep icons 24px (26px in the rail, 28px in the reel column).
- Don't introduce gradients on buttons or text. Don't add a light theme. Don't use emoji outside content glyphs.
