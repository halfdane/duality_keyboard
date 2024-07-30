def miryokufy(keyboard, cirque):          
     from kmk.keys import KC
     from kmk.modules.combos import Combos, Chord, Sequence
     from kmk.modules.layers import Layers;

     from kmk.modules.mouse_keys import MouseKeys; keyboard.modules.append(MouseKeys())
     from kmk.modules.power import Power; keyboard.modules.append(Power())
     from kmk.modules.tapdance import TapDance; keyboard.modules.append(TapDance())
     from kmk.extensions.media_keys import MediaKeys; keyboard.extensions.append(MediaKeys())
     from kmk.modules.capsword import CapsWord; keyboard.modules.append(CapsWord())
     from kmk.modules.holdtap import HoldTap; keyboard.modules.append(HoldTap())

     from kmk.utils import Debug; debug = Debug(__name__)

     layers = Layers()
     combos = Combos() 
     keyboard.modules.append(layers)

     # homerow mods
     def hm(tap, mod):
          return KC.HT(tap, mod, prefer_hold=False, tap_interrupted=True, tap_time=125)

     # layer tap
     def lt(layer, tap):
          return KC.HT(tap, KC.MO(layer), prefer_hold=True, tap_interrupted=False, tap_time=200)

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

     LEFT=0
     RIGHT=1

     if cirque is not None:
          cirque.on_touch_start(lambda: layers.activate_layer(keyboard, BUTTON))
          cirque.on_touch_end(lambda: layers.deactivate_layer(keyboard, BUTTON))

     thumbs = [None] * 10
     # the thumb buttons and how they combine in different layers
     #                 LEFT_1           LEFT_2             LEFT_COMBO           RIGHT_2           RIGHT_1          RIGHT_
     thumbs[BASE] = [ [lt(NAV, KC.SPC), lt(MEDIA, KC.TAB), lt(MOUSE, KC.ESC)], [lt(NUM, KC.BSPC), lt(FUN, KC.ENT), lt(SYM, KC.DEL)] ]
     thumbs[EXTRA] = [ [lt(NAV, KC.SPC), lt(MEDIA, KC.TAB), lt(MOUSE, KC.ESC)], [lt(NUM, KC.BSPC), lt(FUN, KC.ENT), lt(SYM, KC.DEL)] ]
     thumbs[TAP] = [ [lt(NAV, KC.SPC), lt(MEDIA, KC.TAB), lt(MOUSE, KC.ESC)], [lt(NUM, KC.BSPC), lt(FUN, KC.ENT), lt(SYM, KC.DEL)] ]
     thumbs[BUTTON] = [ [KC.MB_LMB, KC.MB_RMB, KC.MB_MMB], [KC.MB_LMB, KC.MB_RMB, KC.MB_MMB] ]
     thumbs[NAV] = [ [lt(NAV, KC.NO), lt(MEDIA, KC.NO), lt(MOUSE, KC.NO)], [lt(NUM, KC.BSPC), lt(FUN, KC.ENT), lt(SYM, KC.DEL)] ]
     thumbs[MOUSE] = [ [lt(NAV, KC.MB_LMB), lt(MEDIA, KC.MB_RMB), lt(MOUSE, KC.MB_MMB)], [lt(NUM, KC.MB_LMB), lt(FUN, KC.MB_RMB), lt(SYM, KC.MB_MMB)] ]
     
     combos.combos = [
          Chord((thumb_layer[side][0], thumb_layer[side][1]), thumb_layer[side][2], timeout=200) 
          for thumb_layer in thumbs if thumb_layer is not None 
          for side in [LEFT, RIGHT]
     ]
     keyboard.modules.append(combos)


     keyboard.keymap = [None] * 10
     
     CL = BASE
     keyboard.keymap[CL] =  [
          KC.Q,               KC.W,               KC.F,               KC.P,               KC.B,               KC.J,          KC.L,               KC.U,               KC.Y,               KC.QUOT,
          hm(KC.A, KC.LGUI),  hm(KC.R, KC.LALT),  hm(KC.S, KC.LCTL),  hm(KC.T, KC.LSFT),  KC.G,               KC.M,          hm(KC.N, KC.RSFT),  hm(KC.E, KC.RCTL),  hm(KC.I, KC.LALT),  hm(KC.O, KC.RGUI),
          KC.Z,               hm(KC.X, KC.RALT),  KC.C,               KC.D,               KC.V,               KC.K,          KC.H,               KC.COMM,            hm(KC.DOT, KC.RALT), KC.SLSH,
                                                            thumbs[CL][LEFT][0], thumbs[CL][LEFT][1],         thumbs[CL][RIGHT][1], thumbs[CL][RIGHT][0] 
     ]
     CL = EXTRA
     keyboard.keymap[CL] =  [
          KC.Q,               KC.W,               KC.E,               KC.R,               KC.T,               KC.Y,          KC.U,               KC.I,               KC.O,               KC.P,
          hm(KC.A, KC.LGUI),  hm(KC.S, KC.LALT),  hm(KC.D, KC.LCTL),  hm(KC.F, KC.LSFT),  KC.G,               KC.H,          hm(KC.J, KC.RSFT),  hm(KC.K, KC.RCTL),  hm(KC.L, KC.LALT),  hm(KC.QUOT, KC.RGUI),
          KC.Z,               hm(KC.X, KC.RALT),  KC.C,               KC.V,               KC.B,               KC.N,          KC.M,               KC.COMM,            hm(KC.DOT, KC.RALT), KC.SLSH,
                                                            thumbs[CL][LEFT][0], thumbs[CL][LEFT][1],         thumbs[CL][RIGHT][1], thumbs[CL][RIGHT][0] 
     ]
     CL = TAP
     keyboard.keymap[CL] =  [
          KC.Q,               KC.W,               KC.F,               KC.P,               KC.B,               KC.J,          KC.L,               KC.U,               KC.Y,               KC.QUOT,
          KC.A,               KC.R,               KC.S,               KC.T,               KC.G,               KC.M,          KC.N,               KC.E,               KC.I,               KC.O,
          KC.Z,               KC.X,               KC.C,               KC.D,               KC.V,               KC.K,          KC.H,               KC.COMM,            KC.DOT,             KC.SLSH,
                                   thumbs[CL][LEFT][0], thumbs[CL][LEFT][1],         thumbs[CL][RIGHT][1], thumbs[CL][RIGHT][0] 
     ]
     CL = BUTTON
     keyboard.keymap[CL] =  [
          KC.NO,    KC.LSFT(KC.DEL), KC.LCTL(KC.INS), KC.LSFT(KC.INS), KC.NO,        KC.NO,     KC.RSFT(KC.INS), KC.RCTL(KC.INS), KC.RSFT(KC.DEL), KC.NO,
          KC.LGUI,        KC.LALT,       KC.LCTL,       KC.LSFT,       KC.NO,        KC.NO,     KC.RSFT,         KC.RCTL,         KC.LALT,         KC.RGUI,
          KC.NO,    KC.LSFT(KC.DEL), KC.LCTL(KC.INS), KC.LSFT(KC.INS), KC.NO,        KC.NO,     KC.RSFT(KC.INS), KC.RCTL(KC.INS), KC.RSFT(KC.DEL), KC.NO,
                                    thumbs[CL][LEFT][0], thumbs[CL][LEFT][1],         thumbs[CL][RIGHT][1], thumbs[CL][RIGHT][0] 
     ]
     CL = NAV
     keyboard.keymap[CL] =  [
          dtd(KC.RELOAD), dtd(KC.DF(2)), dtd(KC.DF(1)), dtd(KC.DF(0)), dtd(KC.TO(0)),     KC.NO,                               KC.LSFT(KC.INS), KC.LCTL(KC.INS), KC.LSFT(KC.DEL), KC.NO,
          KC.LGUI,        KC.LALT,       KC.LCTL,       KC.LSFT,       KC.NO,             KC.CW, KC.LEFT,         KC.DOWN,         KC.UP,           KC.RGHT,
          KC.NO,          KC.RALT,       KC.LCTL(KC.INS), KC.LSFT(KC.INS), KC.NO,             KC.INS,                              KC.HOME,         KC.PGDN,         KC.PGUP,         KC.END,
                                         thumbs[CL][LEFT][0], thumbs[CL][LEFT][1],         thumbs[CL][RIGHT][1], thumbs[CL][RIGHT][0] 
     ]
     CL = MOUSE
     keyboard.keymap[CL] =  [
          dtd(KC.RELOAD), dtd(KC.DF(2)), dtd(KC.DF(1)), dtd(KC.DF(0)), dtd(KC.TO(0)),     KC.NO,     KC.LSFT(KC.INS), KC.LCTL(KC.INS), KC.LSFT(KC.DEL), KC.NO,
          KC.LGUI,        KC.LALT,       KC.LCTL,       KC.LSFT,       KC.NO,     KC.NO,     KC.MS_LT,        KC.MS_DN,        KC.MS_UP,        KC.MS_RT,
          KC.NO,          KC.RALT,       dtd(KC.DF(8)), dtd(KC.DF(5)), KC.NO,     KC.NO,     KC.NO,           KC.MW_DN,        KC.MW_UP,        KC.NO,
                                    thumbs[CL][LEFT][0], thumbs[CL][LEFT][1],         thumbs[CL][RIGHT][1], thumbs[CL][RIGHT][0] 
     ]
     keyboard.keymap[MEDIA] =  [
          dtd(KC.RELOAD), dtd(KC.DF(2)), dtd(KC.DF(1)), dtd(KC.DF(0)), dtd(KC.TO(0)),     KC.NO,     KC.NO,   KC.NO,   KC.NO,   KC.NO,
          KC.LGUI,        KC.LALT,       KC.LCTL,       KC.LSFT,       KC.NO,     KC.PS_TOG, KC.MPRV, KC.VOLD, KC.VOLU, KC.MNXT,
          KC.NO,          KC.RALT,       dtd(KC.DF(9)), dtd(KC.DF(6)), KC.NO,     KC.HID,    KC.NO,   KC.NO,   KC.NO,   KC.NO,
                                                        KC.NO,         KC.NO,     KC.MSTP,   KC.MUTE
     ]
     keyboard.keymap[NUM] =  [
          KC.LBRC,  KC.N7, KC.N8,  KC.N9, KC.RBRC,     dtd(KC.TO(0)),      dtd(KC.DF(0)), dtd(KC.DF(1)), dtd(KC.DF(2)), dtd(KC.RELOAD),
          KC.SCLN,  KC.N4, KC.N5,  KC.N6, KC.EQL,      KC.NO, KC.LSFT,       KC.LCTL,       KC.LALT,       KC.LGUI,
          KC.GRV,   KC.N1, KC.N2,  KC.N3, KC.BSLS,     KC.NO, dtd(KC.DF(7)), dtd(KC.DF(4)), KC.RALT,       KC.NO,
                                   KC.N0, KC.MINS,     KC.NO, KC.NO,
     ]
     keyboard.keymap[SYM] =  [
          KC.LCBR, KC.AMPR, KC.ASTR, KC.LPRN, KC.RCBR,      dtd(KC.TO(0)), dtd(KC.DF(0)), dtd(KC.DF(1)), dtd(KC.DF(2)), dtd(KC.RELOAD),
          KC.COLN, KC.DLR,  KC.PERC, KC.CIRC, KC.PLUS,      KC.NO, KC.LSFT,       KC.LCTL,       KC.LALT,       KC.LGUI,
          KC.TILD, KC.EXLM, KC.AT,   KC.HASH, KC.PIPE,      KC.NO, dtd(KC.DF(8)), dtd(KC.DF(5)), KC.RALT,       KC.NO,
                                     KC.RPRN, KC.UNDS,      KC.NO, KC.NO, 
     ]
     keyboard.keymap[FUN] =  [
          KC.F12, KC.F7,  KC.F8,  KC.F9,  KC.PSCR,       dtd(KC.TO(0)), dtd(KC.DF(0)), dtd(KC.DF(1)), dtd(KC.DF(2)), dtd(KC.RELOAD),
          KC.F11, KC.F4,  KC.F5,  KC.F6,  KC.SLCK,       KC.NO, KC.LSFT,       KC.LCTL,       KC.LALT,       KC.LGUI,
          KC.F10, KC.F1,  KC.F2,  KC.F3,  KC.PAUS,       KC.NO, dtd(KC.DF(9)), dtd(KC.DF(6)), KC.RALT,       KC.NO,
                                  KC.SPC, KC.TAB,        KC.NO, KC.NO,
     ]

     layer_names_list = [
     "Base", "Extra", "Tap", "Button", "Nav", "Mouse", "Media", "Num", "Sym", "Fun",
     ]


