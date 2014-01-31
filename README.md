# nine

A Python-ish programming language that targets the CLR.

A few colleagues and I wrote this back in 2005 for a software engineering class.  It's written in Python.

The language looks a fair bit like Python, but is statically typed and targets the CLR.

# What does the language look like?

A lot like Python. :)

```python
class Quad:
    var points as array(Vertex)

    static def New(v1 as Vertex, v2 as Vertex, v3 as Vertex, v4 as Vertex) as Quad:
        var q = Quad()
        q.points = array(Vertex, 4)
        q.points[0] = v1
        q.points[1] = v2
        q.points[2] = v3
        q.points[3] = v4
        return q

    def Draw():
        for p in self.points:
            p.Draw()
```

If you're interested in further detail, check out the test suite in `ninec/tests`.  By
and large, the tests compile and run programs that exercise just about
every corner of the syntax.

# Running the Code

I've gotten all the tests to run green on IronPython 2.9.9a0 on
Mono 3.2.5 on OSX.  I really hope it will also run on Windows.
