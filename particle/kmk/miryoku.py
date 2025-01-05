def miryokufy(keyboard, motionscanner):  
     from kmk.keys import KC
     from kmk.modules.combos import Combos, Chord, Sequence
     from kmk.modules.layers import Layers

     from kmk.modules.mouse_keys import MouseKeys; keyboard.modules.append(MouseKeys())
     from kmk.modules.power import Power; keyboard.modules.append(Power())
     from kmk.modules.tapdance import TapDance; keyboard.modules.append(TapDance())
     from kmk.extensions.media_keys import MediaKeys; keyboard.extensions.append(MediaKeys())
     from kmk.modules.holdtap import HoldTap; keyboard.modules.append(HoldTap())
     from kmk.modules.capsword import CapsWord; keyboard.modules.append(CapsWord()) 

     layers = Layers()
     combos = Combos() 
     keyboard.modules.append(layers)

     # homerow mods
     def hm(tap, mod):
          return KC.HT(tap, mod, prefer_hold=False, tap_interrupted=True, tap_time=150)

     # layer tap
     def lt(layer, tap):
          return KC.HT(tap, KC.MO(layer), prefer_hold=True, tap_interrupted=False, tap_time=150)

     # home row mod tap dance
     def hmtd(tap, hold, second_tap):
          return KC.TD(hm(tap, hold), second_tap, tap_time=200) 

     # dummy tapdance: first tap is noop
     def dtd(second_tap):
          return KC.TD(KC.NO, second_tap, tap_time=200)
     
     BASE = 0 
     EXTRA = 1
     TAP = 2
     BUTTON = 3
     NAV = 4
     MOUSE = 5 
     MEDIA = 6
     NUM = 7
     SYM = 8
     FUN = 9

     if motionscanner is not None:
          motionscanner.set_touch_start_callback(lambda: layers.activate_layer(keyboard, BUTTON))
          motionscanner.set_touch_end_callback(lambda: layers.deactivate_layer(keyboard, BUTTON))

     both_lft = (17, 11)
     both_rgt = (29, 35)
     combos.combos = [
          Chord(both_lft, lt(MOUSE, KC.ESC), match_coord=True),
          Chord(both_rgt, lt(SYM, KC.DEL), match_coord=True)
     ]
     keyboard.modules.append(combos)

     keyboard.keymap = [None] * 10
     keyboard.keymap[BASE] =  [
          KC.Q,              KC.W,              KC.F,              KC.P,              KC.B,
          hm(KC.A, KC.LGUI), hm(KC.R, KC.LALT), hm(KC.S, KC.LCTL), hm(KC.T, KC.LSFT), KC.G,
          KC.Z,              hm(KC.X, KC.RALT), KC.C,              KC.D,              KC.V,
          lt(NAV, KC.SPC),   lt(MEDIA, KC.TAB),

          KC.J,          KC.L,               KC.U,               KC.Y,                KC.QUOT,
          KC.M,          hm(KC.N, KC.RSFT),  hm(KC.E, KC.RCTL),  hm(KC.I, KC.LALT),   hm(KC.O, KC.RGUI),
          KC.K,          KC.H,               KC.COMM,            hm(KC.DOT, KC.RALT), KC.SLSH,
          lt(NUM, KC.ENT), lt(FUN, KC.BSPC)
     ]
     keyboard.keymap[EXTRA] =  [
          KC.Q,               KC.W,               KC.E,               KC.R,               KC.T,
          hm(KC.A, KC.LGUI),  hm(KC.S, KC.LALT),  hm(KC.D, KC.LCTL),  hm(KC.F, KC.LSFT),  KC.G,
          KC.Z,               hm(KC.X, KC.RALT),  KC.C,               KC.V,               KC.B,
          lt(NAV, KC.SPC), lt(MEDIA, KC.TAB),

          KC.Y,          KC.U,               KC.I,               KC.O,               KC.P,
          KC.H,          hm(KC.J, KC.RSFT),  hm(KC.K, KC.RCTL),  hm(KC.L, KC.LALT),  hm(KC.QUOT, KC.RGUI),
          KC.N,          KC.M,               KC.COMM,            hm(KC.DOT, KC.RALT), KC.SLSH,
          lt(NUM, KC.ENT), lt(FUN, KC.BSPC)
     ]
     keyboard.keymap[TAP] =  [
          KC.Q,               KC.W,               KC.F,               KC.P,               KC.B,
          KC.A,               KC.R,               KC.S,               KC.T,               KC.G,
          KC.Z,               KC.X,               KC.C,               KC.D,               KC.V,
          lt(NAV, KC.SPC), lt(MEDIA, KC.TAB),

          KC.J,          KC.L,               KC.U,               KC.Y,               KC.QUOT,
          KC.M,          KC.N,               KC.E,               KC.I,               KC.O,
          KC.K,          KC.H,               KC.COMM,            KC.DOT,             KC.SLSH,
          lt(NUM, KC.ENT), lt(FUN, KC.BSPC)
     ]
     keyboard.keymap[BUTTON] =  [
          dtd(KC.DF(0)),    KC.LSFT(KC.DEL), KC.LCTL(KC.INS), KC.LSFT(KC.INS), KC.NO,
          KC.LGUI,        KC.LALT,       KC.LCTL,       KC.LSFT,       KC.NO,
          KC.NO,    KC.LSFT(KC.DEL), KC.LCTL(KC.INS), KC.LSFT(KC.INS), KC.MB_MMB,
          KC.MB_LMB, KC.MB_RMB,

          KC.NO,     KC.RSFT(KC.INS), KC.RCTL(KC.INS), KC.RSFT(KC.DEL), dtd(KC.DF(0)),
          KC.NO,     KC.RSFT,         KC.RCTL,         KC.LALT,         KC.RGUI,
          KC.NO,     KC.RSFT(KC.INS), KC.RCTL(KC.INS), KC.RSFT(KC.DEL), KC.NO,
          KC.MB_LMB, KC.MB_RMB
     ]
     keyboard.keymap[NAV] =  [
          dtd(KC.RELOAD), dtd(KC.DF(2)), dtd(KC.DF(1)), dtd(KC.DF(0)), dtd(KC.TO(0)),
          KC.LGUI,        KC.LALT,       KC.LCTL,       KC.LSFT,       KC.NO,        
          KC.NO,          KC.RALT,       KC.LCTL(KC.INS), KC.LSFT(KC.INS), KC.NO,
          lt(NAV, KC.NO), lt(MEDIA, KC.NO), 

          KC.NO, KC.LSFT(KC.INS), KC.LCTL(KC.INS), KC.LSFT(KC.DEL), KC.NO,
          KC.CW, KC.LEFT,         KC.DOWN,         KC.UP,           KC.RGHT,
          KC.INS,KC.HOME,         KC.PGDN,         KC.PGUP,         KC.END,
          lt(NUM, KC.ENT), lt(FUN, KC.BSPC)
     ]
     keyboard.keymap[MOUSE] =  [
          dtd(KC.RELOAD), dtd(KC.DF(2)), dtd(KC.DF(1)), dtd(KC.DF(0)), dtd(KC.TO(0)),
          KC.LGUI,        KC.LALT,       KC.LCTL,       KC.LSFT,       KC.NO,
          KC.NO,          KC.RALT,       dtd(KC.DF(8)), dtd(KC.DF(5)), KC.NO,
          KC.NO,         KC.NO,

          KC.NO,     KC.LSFT(KC.INS), KC.LCTL(KC.INS), KC.LSFT(KC.DEL), KC.NO,
          KC.NO,     KC.MS_LT,        KC.MS_DN,        KC.MS_UP,        KC.MS_RT,
          KC.NO,     KC.NO,           KC.MW_DN,        KC.MW_UP,        KC.NO,
          KC.NO,         KC.NO
     ]
     keyboard.keymap[MEDIA] =  [
          KC.RESET, dtd(KC.DF(2)), dtd(KC.DF(1)), dtd(KC.DF(0)), dtd(KC.TO(0)),
          KC.LGUI,        KC.LALT,       KC.LCTL,       KC.LSFT,       KC.NO,
          KC.NO,          KC.RALT,       dtd(KC.DF(9)), dtd(KC.DF(6)), KC.NO,
          KC.NO,         KC.NO,

          KC.NO,     KC.NO,   KC.NO,   KC.NO,   KC.NO,
          KC.PS_TOG, KC.MPRV, KC.VOLD, KC.VOLU, KC.MNXT,
          KC.HID,    KC.NO,   KC.NO,   KC.NO,   KC.NO,
          KC.MSTP,   KC.MUTE
     ]
     keyboard.keymap[NUM] =  [
          KC.LBRC,  KC.N7, KC.N8,  KC.N9, KC.RBRC,
          KC.SCLN,  KC.N4, KC.N5,  KC.N6, KC.EQL, 
          KC.GRV,   KC.N1, KC.N2,  KC.N3, KC.BSLS,
          KC.N0, KC.MINS,

          dtd(KC.TO(0)),      dtd(KC.DF(0)), dtd(KC.DF(1)), dtd(KC.DF(2)), KC.RESET,
          KC.NO, KC.LSFT,       KC.LCTL,       KC.LALT,       KC.LGUI,
          KC.NO, dtd(KC.DF(7)), dtd(KC.DF(4)), KC.RALT,       KC.NO,
          KC.NO, KC.NO,
     ]
     keyboard.keymap[SYM] =  [
          KC.LCBR, KC.AMPR, KC.ASTR, KC.LPRN, KC.RCBR,
          KC.COLN, KC.DLR,  KC.PERC, KC.CIRC, KC.PLUS,
          KC.TILD, KC.EXLM, KC.AT,   KC.HASH, KC.PIPE,
          KC.RPRN, KC.UNDS,

          dtd(KC.TO(0)), dtd(KC.DF(0)), dtd(KC.DF(1)), dtd(KC.DF(2)), dtd(KC.RELOAD),
          KC.NO, KC.LSFT,       KC.LCTL,       KC.LALT,       KC.LGUI,
          KC.NO, dtd(KC.DF(8)), dtd(KC.DF(5)), KC.RALT,       KC.NO,
          KC.NO, KC.NO, 
     ]
     keyboard.keymap[FUN] =  [
          KC.F12, KC.F7,  KC.F8,  KC.F9,  KC.PSCR,
          KC.F11, KC.F4,  KC.F5,  KC.F6,  KC.SLCK,
          KC.F10, KC.F1,  KC.F2,  KC.F3,  KC.PAUS,
          KC.SPC, KC.TAB,

          dtd(KC.TO(0)), dtd(KC.DF(0)), dtd(KC.DF(1)), dtd(KC.DF(2)), dtd(KC.RELOAD),
          KC.NO, KC.LSFT,       KC.LCTL,       KC.LALT,       KC.LGUI,
          KC.NO, dtd(KC.DF(9)), dtd(KC.DF(6)), KC.RALT,       KC.NO,
          KC.NO, KC.NO,
     ]

