# EASY Language

---

## Getting Started

```
python s.py myprogram.epp
```

No file? Runs the built-in demo:

```
python s.py
```

---

## Syntax

### Print

```
say "Hello, world!"
say myVariable
say "The answer is " + 42
```

### Variables & Math

```
x = 10 + 5
y = x * 2
z = 100 / 4
remainder = 10 % 3
```

### Comments

```
# This is a comment
```

---

## Conditions

### if / otherwise

```
if x > 10: say "big"
otherwise: say "small"
```

### Natural language

```
if x is bigger than 10 then: say "big"
if x is smaller than 5 then: say "small"
if x is equals 7 then: say "lucky"
```

### Comparisons

| Symbol | Meaning |
|--------|---------|
| `==` | equals |
| `!=` | not equals |
| `>` | greater than |
| `<` | less than |
| `>=` | greater than or equal |
| `<=` | less than or equal |

### Boolean logic

```
if x > 0 and y > 0: say "both positive"
if x == 0 or y == 0: say "one is zero"
if not done: say "still going"
```

---

## Loops

### repeat

```
repeat 5: say "hello"
```

### while

```
count = 0
while count < 10: count = count + 1
```

---

## User Input

```
ask "What is your name?" -> name
say "Hello, " + name
```

---

## GUI

### Window

```
window "My App"
```

### Label

```
label "Enter your name:"
label "Warning!" color "red"
```

### Textbox

```
textbox -> username
```

### Slider

```
slider 0 to 100 -> volume
```

### Checkbox

```
checkbox "Enable sound" -> soundOn
```

### Display

```
display -> screen
```

### Button - single line

```
button "Click me": say "Hello!"
button "Reset" color "red": score = 0
```

### Button - multi-line

```
button "Submit" color "green": do
    say "Name: " + username
    say "Volume: " + volume
end
```

---

## compute

```
compute screen -> screen
```

---

## Colors

`"red"` `"green"` `"blue"` `"orange"` `"yellow"` `"purple"` `"pink"` `"white"` `"black"` `"gray"`

---

## Files

| File | Description |
|------|-------------|
| `s.py` | The EASY interpreter |
| `calculator.epp` | Keypad calculator |
| `example.epp` | All features showcased |

---

## Limitations

- `while` and `repeat` are single-line only
- All variables are global
- Textbox values are strings, use sliders or `compute` when you need numbers
- No functions yet
