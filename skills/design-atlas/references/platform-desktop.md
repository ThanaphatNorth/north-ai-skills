# Platform: Desktop (macOS, Windows, Linux, desktop-class web apps)

> Read when: designing or reviewing a macOS/Windows/Linux app, an Electron/Tauri/Flutter/.NET MAUI/Compose Multiplatform desktop app, or a "pro" web app that should behave like desktop software (Figma/Linear/Notion-style) — menus, toolbars, shortcuts, windows, sidebars and multi-pane layouts, data tables, density, command palettes, drag and drop, tray/menu bar extras, sync status, auto-update.

**Contents:** Platform snapshot · macOS (HIG, Liquid Glass) · Windows 11 (Fluent 2, WinUI 3) · Linux (GNOME/libadwaita) · Per-OS conventions · Cross-platform frameworks · Desktop UX patterns · Desktop-class web apps · Pitfalls · Sources

Siblings: `platform-web.md` (responsive web, Baseline CSS), `platform-mobile.md` (iPad, touch), `accessibility.md` (keyboard focus, WCAG), `design-systems.md` (tokens across platforms), `product-patterns.md` (empty states, onboarding).

---

## Platform snapshot (as of 2026-10-10)

| Platform | Current design language | Notes |
|---|---|---|
| macOS 26 Tahoe (2025) → macOS 27 (2026) | Liquid Glass: floating glass sidebars and toolbars, capsule large controls, layered app icons | Apps linked against the macOS 27 SDK ignore `UIDesignRequiresCompatibility` (no opting out of the new look); iOS 27 adds a user glass-opacity setting ("ultra clear" → "fully tinted"; macOS parity unverified) |
| Windows 11 | Fluent 2 via WinUI 3 / Windows App SDK: Mica, Mica Alt, Acrylic, Segoe UI Variable, rounded corners | Material falls back to solid colour when transparency is off, on battery saver, low-end hardware, or inactive windows |
| GNOME (Linux) | libadwaita + GNOME HIG: header bars, primary menu, adaptive layouts | KDE/Qt apps follow different conventions; match the target desktop |

---

## macOS (HIG)

### Type, sizes, controls

| macOS text style | pt / line | macOS text style | pt / line |
|---|---|---|---|
| Large Title | 26 / 32 | Body | 13 / 16 |
| Title 1 | 22 / 26 | Callout | 12 / 15 |
| Title 2 | 17 / 22 | Subheadline | 11 / 14 |
| Title 3 | 15 / 20 | Footnote / Caption 1 / Caption 2 | 10 / 13 |
| Headline (bold) | 13 / 16 | | |

- Default text 13pt, minimum 10pt; **no Dynamic Type on macOS** — respect the system "Text size" settings where available and never go below 10pt.
- Control hit size: **28×28pt default, 20×20pt minimum**. Control sizes mini/small/medium stay rounded rectangles; **large** is a capsule; new **X-Large** uses Liquid Glass for the most prominent action (`controlSize(.extraLarge)` / `.large`).
- Sidebars float as Liquid Glass; extend content beneath with `backgroundExtensionEffect()`. Prefer the **hard** scroll edge effect for dense macOS content and pinned table headers.

### Menu bar: every command lives in a menu
- Order: **App · File · Edit · Format · View · (app-specific) · Window · Help.** Provide View and Window menus even if sparse.
- Commands left out of the menu bar can't have shortcuts and are invisible to Full Keyboard Access → every toolbar button, context-menu action and palette command must also exist in a menu.
- App menu: About App · Settings… (⌘,) · Services · Hide App (⌘H) · Hide Others (⌥⌘H) · Show All · Quit App (⌘Q).
- Edit menu: Undo/Redo name the action ("Undo Paste", "Redo Typing"); Delete (not "Erase"/"Clear"); Find submenu.
- View menu titles reflect state ("Show Sidebar" ↔ "Hide Sidebar", "Enter/Exit Full Screen").
- **Disable, don't hide** unavailable items so the menu stays learnable.
- **Menu bar extras** (status items): optional and user-enabled; menu bar is 24pt tall; clicking shows a *menu* (not a popover) unless the UI is genuinely complex; also expose actions in the Dock menu.

### Standard shortcuts you must not repurpose (subset)

| Shortcut | Action | Shortcut | Action |
|---|---|---|---|
| ⌘N / ⌘O / ⌘S | New / Open / Save | ⇧⌘S | Duplicate / Save As |
| ⌘W / ⌥⌘W | Close window / all | ⌘Q | Quit |
| ⌘Z / ⇧⌘Z | Undo / Redo | ⌘X ⌘C ⌘V | Cut / Copy / Paste |
| ⌥⇧⌘V | Paste and match style | ⌘A | Select all |
| ⌘F / ⌘G / ⇧⌘G | Find / next / previous | ⌘E | Use selection for Find |
| ⌘, | Settings | ⌘? | Help menu |
| ⌘. | Cancel operation | ⌘M | Minimize |
| ⌘` | Next window of app | ⌃⌘F | Enter full screen |
| ⌥⌘I | Show inspector | ⌥⌘T | Show/hide toolbar |
| ⌘P | Print | ⌘H / ⌥⌘H | Hide app / others |

- Modifier display order: **⌃ Control, ⌥ Option, ⇧ Shift, ⌘ Command.** Prefer ⌘ as the base; ⇧ for a related variant; ⌥ sparingly; avoid ⌃ (system uses it).
- Write ⌘? not ⇧⌘/; let the system localize and mirror shortcuts for other keyboard layouts.

### Windows, toolbars, settings, inspectors
- **Windows:** one main window, one key window; inactive windows lose colour in the traffic lights and vibrancy — custom chrome must reproduce these states (better: don't customize chrome). Restore window size, position, open documents and selection on relaunch. Avoid bottom bars for critical actions (windows get dragged partly off-screen).
- **Toolbars:** ≤3 groups; group by function and frequency; don't mix text and symbol buttons in one group; one primary action, trailing; every item also in a menu; let users customize in long-session apps (leading back/sidebar/title items are fixed).
- **Settings window:** opened via App menu "Settings…" ⌘, (not a toolbar button); toolbar of panes, non-customizable; window title = current pane (single pane: "App Name Settings"); reopens on the last pane; minimize/zoom dimmed; window sizes itself to each pane. Don't duplicate system settings (appearance, scrolling, accessibility).
- **Split views:** 2–3 panes (sidebar · content · detail); persistent selection highlight in each pane that drives the next; min/max widths so dividers stay grabbable; thin 1pt divider; every collapsible pane can be revealed via toolbar button + menu item + shortcut.
- **Sidebars:** ≤2 levels; don't hide by default; icons follow the user's accent colour; row size follows the system sidebar icon size (small/medium/large).
- **Inspector:** trailing-edge pane for properties of the selection (`inspector(isPresented:)`), toggled with ⌥⌘I.

```swift
// macOS 26+: three-column app with native commands
@main struct NotesApp: App {
  @State private var showInspector = false
  @State private var query = ""
  var body: some Scene {
    WindowGroup {
      NavigationSplitView {
        SidebarView().navigationSplitViewColumnWidth(min: 180, ideal: 220)
      } content: { NoteList() } detail: { NoteEditor() }
        .inspector(isPresented: $showInspector) { Inspector() }
        .searchable(text: $query)                     // covers all columns
    }
    .commands {
      SidebarCommands()                               // View ▸ Show/Hide Sidebar
      CommandGroup(replacing: .newItem) {             // File ▸ New Note ⌘N (replaces New Window)
        Button("New Note") { newNote() }.keyboardShortcut("n")
      }
      CommandMenu("Note") {
        Button("Pin Note") { pin() }.keyboardShortcut("p", modifiers: [.command, .shift])
      }
    }
    Settings { SettingsView() }                       // App ▸ Settings… ⌘,
    MenuBarExtra("Quick Note", systemImage: "note.text") { QuickNoteMenu() }
  }
}
```

---

## Windows 11 (Fluent 2, WinUI 3)

### Type ramp (Segoe UI Variable, effective pixels)

| Style | Weight | Size / line |
|---|---|---|
| Caption | Regular | 12 / 16 |
| Body | Regular | 14 / 20 |
| Body Strong | Semibold | 14 / 20 |
| Body Large | Regular | 18 / 24 |
| Subtitle | Semibold | 20 / 28 |
| Title | Semibold | 28 / 36 |
| Title Large | Semibold | 40 / 52 |
| Display | Semibold | 68 / 92 |

- Minimums: 14px Semibold or 12px Regular. Sentence case for all UI text, including titles. Emphasis = Semibold (no Bold/Italic in the ramp). 50–60 characters per line. Thai UI font: **Leelawadee UI**.

### Geometry, spacing, materials

| Token | Value |
|---|---|
| Corner radius | 8px windows, dialogs, flyouts; 4px buttons, inputs, list backplates, bars, tooltips; 0px when maximized/snapped or where straight edges meet (`OverlayCornerRadius` 8, `ControlCornerRadius` 4) |
| Spacing | 8 epx between buttons / button↔flyout / control↔header; 12 epx control↔label and between content areas; 16 epx surface edge↔text; 48 epx indent for controls inside an expander |
| Title bar | 32px standard; **48px** when it hosts a search box or account picture; icon 16×16 placed 16px from edge; title 16px after icon in Caption style |

| Material | Use for | Don't |
|---|---|---|
| **Mica** | Base layer (window backdrop) of long-lived windows; make it show through the title bar | Apply more than once; put on individual controls |
| **Mica Alt** | Base layer when the title bar holds tabs (stronger tint separates tabs from content) | — |
| **Acrylic** (background) | Transient, light-dismiss surfaces: context menus, flyouts, popups (controls do this by default) | Large backgrounds; adjacent acrylic panes (visible seam); accent-coloured text or links on acrylic |
| Acrylic (in-app) | Panes that overlay content (NavigationView compact/minimal when open) | Fixed side panes → use opaque layer |

Content sits on a low-opacity layer brush (`LayerFillColorDefaultBrush`) over Mica; cards for sectioned UIs.

### Title bar behaviour (custom title bars must keep these)
- All empty space and the title text are draggable; double-click toggles maximize; right-click opens the system window menu; icon single-click opens the window menu.
- All title-bar elements go semi-transparent when the window is inactive; follow light/dark and high-contrast (`SystemColors`).
- Caption buttons (min/max/close) stay right-anchored and always fully visible; tabs may occupy the rest of the title bar.

### Navigation and commanding

| Control | Rule |
|---|---|
| NavigationView `Top` | ≤5 equally important top-level categories |
| NavigationView `Auto` (default) | **Left** expanded ≥1008px · **LeftCompact** (icon rail) 641–1007px · **LeftMinimal** (menu button) ≤640px |
| CommandBar | Primary commands in importance order; overflow ("…") holds secondary; dynamic overflow on resize; ≤4 primary commands at 320 epx width; labels to the right of icons on wide windows; icons 20px (bar) / 16px (overflow) |
| Dialog buttons | Accept / Yes / OK **left** of Reject / No / Cancel |
| Context menus | `MenuFlyout` with acrylic; include keyboard accelerators text |

Density: WinUI ships a compact sizing resource dictionary for data-dense apps — apply it per page or app; verify exact control heights for your WinUI version.

---

## Linux (GNOME HIG / libadwaita)
- **Header bar** instead of title bar + menubar: start = main actions (New, Add, Back); centre = window title or a view switcher; end = menus. Few controls; leave blank space for dragging; tooltips on all icon buttons.
- **Primary menu** (`open-menu-symbolic`, tooltip "Main Menu") at the end of the header bar, containing at the bottom: Preferences · Keyboard Shortcuts · Help · About *App* (always). No Close/Quit items.
- Menus 3–12 items, submenus 3–6, no nested submenus; verbs for commands, adjectives for settings.
- Window sizes: support 1024×600px; apps meant for phones must scale down to 360×294px. Use libadwaita adaptive widgets/breakpoints rather than custom ones.

---

## Per-OS conventions (cross-platform apps must switch these)

| Concern | macOS | Windows | GNOME |
|---|---|---|---|
| Primary modifier | ⌘ Command | Ctrl | Ctrl |
| Redo | ⇧⌘Z | Ctrl+Y (also Ctrl+Shift+Z) | Shift+Ctrl+Z |
| Settings | App menu › Settings… ⌘, | Settings page in nav (gear) or File/Tools › Options; Ctrl+, common in modern apps | Primary menu › Preferences (Ctrl+,) |
| Menus | Global menu bar, all commands | In-window menu bar or command bar + "…" | Header bar + primary menu |
| Window controls | Traffic lights, leading (left) | Caption buttons, trailing (right) | Close at trailing end by default |
| Dialog button order | Default action rightmost, Cancel to its left | OK/Accept left of Cancel | Cancel at start, action at end (header-bar dialogs) |
| Full screen | ⌃⌘F | F11 | F11 |
| Close last window | Document apps keep running; utility apps may quit | App exits (unless tray app) | App exits |
| System font | SF Pro (`system-ui`) | Segoe UI Variable | Adwaita/Cantarell via `system-ui` |
| Pointer on buttons | Arrow (no hand cursor) | Arrow | Arrow — hand cursor only for hyperlinks |

---

## Cross-platform desktop frameworks

| Framework | Rendering | Pick when | Watch out |
|---|---|---|---|
| Electron | Bundled Chromium + Node | Web team, rich web UI, need identical rendering everywhere | Size/RAM; must add native menus, title bar, shortcuts per OS yourself |
| Tauri 2 | System webview (WebView2 / WKWebView / WebKitGTK) + Rust | Small binaries, security-minded, web UI | Webview differences across OSes → test CSS on all three |
| Flutter desktop | Own renderer | Shared mobile + desktop codebase | Must add menus (`PlatformMenuBar` on macOS), shortcuts, focus handling, context menus |
| .NET MAUI | Native controls (WinUI on Windows, Mac Catalyst on macOS) | .NET shops, line-of-business | Mac Catalyst feels iPad-like unless tuned |
| Compose Multiplatform | Skia renderer on JVM desktop | Kotlin/Android teams | Native menu bar/tray via its desktop APIs; JVM footprint |
| React Native for Windows/macOS | Native controls | RN teams targeting Windows/macOS | Smaller ecosystem than mobile RN |

**Make it feel native — checklist**
1. **Native application menu** on macOS with standard roles (About, Settings, Hide, Quit, Edit roles so ⌘C/⌘V work in text fields) and app commands mirrored from toolbar/palette.
2. **Window chrome:** macOS `titleBarStyle: 'hiddenInset'` (or `hidden` + `trafficLightPosition`); Windows/Linux keep native caption buttons via `titleBarOverlay`; mark drag areas with `app-region: drag` and interactive elements `no-drag`. Tauri: `data-tauri-drag-region` on each draggable element, or macOS `TitleBarStyle::Transparent` to keep native window behaviours.
3. **Shortcuts per OS:** define accelerators as `CmdOrCtrl+…`; show ⌘ glyphs on Mac, "Ctrl+" text elsewhere.
4. **System font and metrics:** `font-family: system-ui, -apple-system, "Segoe UI Variable Text", "Segoe UI", sans-serif;` body 13px (mac) / 14px (Windows).
5. **Respect system settings:** light/dark (`nativeTheme.themeSource = 'system'` drives `prefers-color-scheme`), high contrast (`shouldUseHighContrastColors` / `forced-colors`), reduced motion, reduced transparency (`prefersReducedTransparency` → swap glass/acrylic for solid).
6. **Desktop behaviours:** native context menus on right-click; no hover-only essentials; arrow cursor on buttons; `user-select: none` on chrome but selectable content; remember window bounds; single-instance lock with "focus existing window"; open links in the default browser.

```js
// Electron (main): per-OS window chrome + theme
const isMac = process.platform === 'darwin';
const win = new BrowserWindow({
  width: 1200, height: 800, minWidth: 720, minHeight: 480,
  titleBarStyle: 'hidden',
  ...(isMac ? { trafficLightPosition: { x: 16, y: 18 } }
            : { titleBarOverlay: { color: '#00000000', symbolColor: '#888', height: 40 } }),
});
nativeTheme.themeSource = 'system';      // renderer prefers-color-scheme follows OS
```

---

## Desktop UX patterns

### Information density
- Desktop users sit close with a precise pointer: default to denser layouts than mobile, but anchor to platform metrics — macOS body 13pt / controls 20–28pt, Windows body 14px / title bar 32px.
- Offer **Comfortable / Compact** density for tables and lists in pro tools; persist per user; keep hit targets ≥24×24px (WCAG 2.5.8) even in compact mode.
- Density comes from removing chrome (borders, card shadows, oversized padding), not from shrinking text below platform minimums.

### Keyboard-first and the command palette
- Every action reachable by: **menu item + keyboard shortcut + command palette entry** (+ context menu where it makes sense).
- Command palette: one global shortcut (⌘K / Ctrl+K is the de-facto convention); opens from anywhere and closes with the same key or Esc, restoring focus; centred; fuzzy, typo-tolerant search with synonyms (show the canonical name when an alias matched); ranked by relevance and recency; context-aware (current selection's actions first); show each command's shortcut beside it so users learn it.
- Lists and tables: arrow keys move, Enter opens/default action, Space toggles selection/Quick Look, type-to-select jumps to matching rows, Esc clears selection or closes the innermost layer.
- Shortcut reference available from Help and via a shortcut (e.g. Figma's Ctrl+Shift+? panel).

### Multi-pane layouts (sidebar – list – detail)

| Window width | Layout |
|---|---|
| Wide (≥ ~1200px) | Sidebar + list + detail (+ optional inspector) |
| Medium | Collapse sidebar to icons, keep list + detail |
| Narrow (< ~720px) | One pane at a time with back navigation |

Persist pane widths and visibility; double-click a divider to reset; keep selection visible when a pane collapses.

### Data grids / tables
- Sticky header row (and sticky first column when wide); click header to sort with a visible arrow (`aria-sort`); second click reverses; **resizable columns** with double-click-to-fit; reorder/hide via a column chooser; save view per user.
- Right-align numbers, use tabular figures (`font-variant-numeric: tabular-nums`), left-align text, consistent decimals and units in the header.
- Selection: checkbox column + click, Shift-click ranges, ⌘/Ctrl-click toggles, ⌘/Ctrl+A all; a **bulk action bar** appears with the count ("3 selected") and clears with Esc.
- Inline edit: Enter or double-click to edit (F2 on Windows), Esc cancels, Tab moves to next cell; validation inline.
- Virtualize long lists; show total count and loading rows; empty and filtered-to-zero states with "Clear filters".

### Drag and drop, context menus, undo
- Drag & drop: lift with a preview, highlight valid targets, show an insertion line, change cursor for copy (⌥ on Mac, Ctrl on Windows) vs move; spring-load folders; Esc cancels. Always provide a non-drag alternative (menu "Move to…", keyboard reorder) — WCAG 2.2 SC 2.5.7.
- Context menus: mirror commands already in menus/toolbars (never the only path); most frequent first; group with separators; show shortcuts; 3–12 items.
- **Undo over confirmation:** for reversible actions (delete to trash, archive, move) act immediately and offer Undo (⌘Z / Ctrl+Z + toast with Undo). Confirm only irreversible, high-cost actions, naming the object ("Delete 'Q3 report' permanently?"). Multi-level undo with named actions.

### Multi-window, tray, notifications
- Let users open any document/item in a new window (menu command, ⌘/Ctrl-click or double-click); list open windows in the Window menu; ⌘` cycles; restore windows on relaunch; macOS window tabs for document apps.
- System tray / menu bar extras only for apps that run in the background (sync, VPN, timers, clipboard): show status at a glance, a short menu, "Open App" and "Quit"; never the only way to reach settings.
- Desktop notifications only when the app is not in focus and the event needs attention; actionable (Reply, Open); grouped; respect Focus/Do Not Disturb; in-app toasts when focused.

### Offline and sync status
- Persistent, quiet indicator in the status bar or title area: **Synced · Syncing… · Offline (changes saved locally) · Conflict**. Show "Last synced 10:42" on hover/click.
- Optimistic local writes; queue and retry; explicit conflict UI showing both versions with "Keep mine / Keep theirs / Keep both".
- Never block editing while offline unless the data truly can't be edited locally.

### Onboarding for pro tools
- Start with a usable sample file or template, not a tour. Empty canvas states show 2–3 primary actions plus "Import".
- Teach shortcuts progressively: show the shortcut in tooltips and menus; palette hints ("Tip: press ⌘K for every command").
- Keep advanced panels collapsed until relevant; remember what the user opened.

### High-DPI and auto-update
- Vector icons (SF Symbols, Segoe Fluent Icons, SVG); raster assets at @1x/@2x (and @3x for iPad). Test Windows at 100%, 125%, 150%, 200% scaling and mixed-DPI multi-monitor; 1px hairlines must stay crisp (use device-pixel borders, not 0.5px hacks on 1x screens).
- Auto-update: check at launch and periodically, download in the background, then a non-blocking prompt **"Restart now / Later"** (call `quitAndInstall()` only on consent); never restart during work; show "What's new" after restart; signed builds (macOS code signing required for update.electronjs.org); skip update checks in development builds.

---

## Desktop-class web apps (Figma, Linear, Notion pattern)

| Trait | What they do | Copy it by |
|---|---|---|
| Keyboard-first | Single-key and chord shortcuts, command menu, visible shortcut hints | Palette + shortcut map + `?`/help panel |
| Instant feel | Local-first state, optimistic updates, no full-page reloads | Client cache + background sync; INP < 200ms |
| App chrome | Sidebar–list–detail, resizable panes, tabs, inspector | Split-pane primitives with persisted sizes |
| Custom context menus | Right-click menus inside canvases/lists | Only where native menus can't express the action; keep keyboard access (Shift+F10 / menu key) |
| Desktop wrappers | Electron apps with native menus, tray, deep links | Add native menus and OS shortcuts; don't just wrap the site |
| Multiplayer | Presence avatars, live cursors, comments | Show who's here; never move content under the user's cursor |

When the product is a web app used for hours a day, apply this file's desktop rules even in the browser; when it's an occasional-use site, follow `platform-web.md` instead.

## Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| ⌘C/⌘V don't work in an Electron text field on macOS | No application menu with Edit roles | Build the native menu with `role: 'editMenu'` items |
| Window can't be dragged / buttons in title bar don't click | Missing `app-region: drag` / `no-drag` (Tauri: drag region not on children) | Mark drag areas and exclude interactive elements |
| Windows app looks flat/greyed when unfocused, devs "fix" it | Mica correctly falls back when inactive | Leave it; design the inactive state |
| Acrylic sidebar looks blotchy, text fails contrast | Acrylic on large/fixed panes, accent text on acrylic | Mica + opaque layer for fixed panes; acrylic only on transient surfaces |
| Feature undiscoverable on Mac | Command only in a toolbar or context menu | Add to a menu with a shortcut |
| Shortcut conflicts on Windows/Linux | Ported ⌘ shortcuts 1:1 to Ctrl, clashing with system/browser keys (Ctrl+W, Ctrl+N in a browser-hosted app) | Per-OS keymap; test in the browser and in the wrapper |
| Custom traffic lights / caption buttons feel broken | Re-implemented chrome missing states (inactive, hover, snap layouts on Windows) | Keep native controls (`titleBarOverlay`, hidden-inset styles) |
| Settings in a modal that loses changes | Web-style modal with Save/Cancel | Dedicated settings window/page; on macOS follow the convention that changes apply as made (no OK/Apply) |
| Users lose layout on relaunch | Pane widths/windows not persisted | Persist window bounds, pane sizes, open tabs, selection |

## Sources

- HIG The menu bar — https://developer.apple.com/design/human-interface-guidelines/the-menu-bar
- HIG Keyboards (standard shortcuts) — https://developer.apple.com/design/human-interface-guidelines/keyboards
- HIG Windows — https://developer.apple.com/design/human-interface-guidelines/windows
- HIG Settings — https://developer.apple.com/design/human-interface-guidelines/settings
- HIG Sidebars — https://developer.apple.com/design/human-interface-guidelines/sidebars
- HIG Split views — https://developer.apple.com/design/human-interface-guidelines/split-views
- HIG Toolbars — https://developer.apple.com/design/human-interface-guidelines/toolbars
- HIG Typography — https://developer.apple.com/design/human-interface-guidelines/typography
- HIG Accessibility (control sizes) — https://developer.apple.com/design/human-interface-guidelines/accessibility
- WWDC25 Build a SwiftUI app with the new design — https://developer.apple.com/videos/play/wwdc2025/323/
- WWDC25 Get to know the new design system — https://developer.apple.com/videos/play/wwdc2025/356/
- Apple Developer Forums: UIDesignRequiresCompatibility and the 27 SDKs — https://developer.apple.com/forums/thread/832543
- Microsoft Learn: Mica — https://learn.microsoft.com/en-us/windows/apps/design/style/mica
- Microsoft Learn: Acrylic — https://learn.microsoft.com/en-us/windows/apps/design/style/acrylic
- Microsoft Learn: Title bar — https://learn.microsoft.com/en-us/windows/apps/design/basics/titlebar-design
- Microsoft Learn: Typography in Windows — https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/typography
- Microsoft Learn: Content layout and spacing — https://learn.microsoft.com/en-us/windows/apps/design/basics/content-basics
- Microsoft Learn: Geometry in Windows 11 — https://learn.microsoft.com/en-us/windows/apps/design/signature-experiences/geometry
- Microsoft Learn: NavigationView — https://learn.microsoft.com/en-us/windows/apps/develop/ui/controls/navigationview
- Microsoft Learn: Command bar — https://learn.microsoft.com/en-us/windows/apps/design/controls/command-bar
- GNOME HIG: Header bars — https://developer.gnome.org/hig/patterns/containers/header-bars.html
- GNOME HIG: Adaptive — https://developer.gnome.org/hig/guidelines/adaptive.html
- GNOME HIG: Menus — https://developer.gnome.org/hig/patterns/controls/menus.html
- Electron: Custom title bar — https://www.electronjs.org/docs/latest/tutorial/custom-title-bar
- Electron: nativeTheme — https://www.electronjs.org/docs/latest/api/native-theme
- Electron: Updating applications — https://www.electronjs.org/docs/latest/tutorial/updates
- Tauri 2: Window customization — https://v2.tauri.app/learn/window-customization/
- Superhuman: How to build a remarkable command palette — https://blog.superhuman.com/how-to-build-a-remarkable-command-palette/
- Figma Help: Use shortcuts and quick actions — https://help.figma.com/hc/en-us/articles/360040328653-Use-shortcuts-and-quick-actions
- WCAG 2.2 Understanding 2.5.8 Target Size (Minimum) — https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
