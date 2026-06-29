# e-ink-timer
pi pico &amp; inky pack (discontinued) 


# components
https://shop.pimoroni.com/products/pico-inky-pack
https://thepihut.com/blogs/raspberry-pi-tutorials/raspberry-pi-pico-getting-started-guide

# set-up steps for inky pack
1. https://github.com/pimoroni/pimoroni-pico/releases/latest/ download this
2. connect pi-pico to computer while holding down the bootsel button
3. drag download (.uf2) file onto pico
4. https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/examples/pico_inky run one of these examples to test
 - use Thonny to run
 - (configure correct pi version in bottom right of IDE)

^ this is just because I know I'll forget if I have to do it from scratch and cba with the extensive scrolling/clicking to get this info

# design for the project
what can you do with pico and e-ink?
- hoping to connect this to a larger project later
- interested in creating seperation from "phone as single tool" because its so easy to then be distracted by it
- thinking of making it a timer for now
- the pack has three button so I'm imagining how I can branch with three functions

## ux design

home: clock (with screen saver function / only displays on button wake) / wheel display?
menu : option a/b/c
       timer / stopwatch/ eras
  timer : 5m / 25m / custom (on completion flash display)
      custom: increase / decrease / start
  stopwatch : start/stop / back / lap
  eras : wheel of year / time left in the work day

on all if double press "b" go back a menu option

thats all for now

### questions to ask
? does the menu make sense / are these the correct functions
? can we go to blank on disconnect
? splash screen
? can i power with a switch somehow?
? case 


# working with picos
- ide is Thonny
- code needs to be saved as main.py on the pico to run everytime power connects
- thonny checklist
- menu flow diagram: `menu-map.md`