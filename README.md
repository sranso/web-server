## Create web server

First, I followed [this tutorial](https://ruslanspivak.com/lsbaws-part1/) (parts 1-3). Then, I went through it a second time, [hiding the code](###hiding-the-code) and implementing everything on my own (hence the dir `on-my-own`).

The impetus to work on this project happened to be succinctly described in the tutorial by Ruslan:
>I believe to become a better developer you MUST get a better understanding of the underlying software systems you use on a daily basis and that includes programming languages, compilers and interpreters, databases and operating systems, web servers and web frameworks. And, to get a better and deeper understanding of those systems you MUST re-build them from scratch, brick by brick, wall by wall.

### Hiding the code
```javascript
function t() {
  var el = $('.highlight');
  var isV = Number(el.css('opacity'))
    isV ? el.css('opacity', 0) : el.css('opacity', 1);
  return isV ? 'hidden!' : 'visible!';
}
```
