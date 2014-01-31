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

# Running the Code

I promise I have absolutely no idea.  It requires [Python for .NET](http://pythonnet.sourceforge.net/) to run and requires
Python 2.4 or something like that.  Some updating will obviously be necessary.
