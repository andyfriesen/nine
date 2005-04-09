
using Tao.Sdl;
using Tao.OpenGl;

public class SDL_Event {
    internal SDL_Event(int type) {
        this.type = type;
    }

    public int Type {
        get { return type; }
    }

    int type;
}

public sealed class SDL {
    private SDL() { }

    public static int OPENGL = Sdl.SDL_OPENGL;
    public static int QUIT = Sdl.SDL_QUIT;

    public static System.IntPtr SetVideoMode(int xres, int yres, int bpp, int flags) {
        return Sdl.SDL_SetVideoMode(xres, yres, bpp, flags);
    }

    public static void SetCaption(string s) {
        Sdl.SDL_WM_SetCaption(s, "");
    }

    public static SDL_Event PollEvent() {
        Sdl.SDL_Event evt;
        Sdl.SDL_PollEvent(out evt);
        return new SDL_Event(evt.type);
    }

    public static void Quit() {
        Sdl.SDL_Quit();
    }
}

public sealed class GL {
    private GL() { }

    public static void SwapBuffers() {
        Sdl.SDL_GL_SwapBuffers();
    }

    public static int COLOR_BUFFER_BIT = Gl.GL_COLOR_BUFFER_BIT;
    public static int DEPTH_BUFFER_BIT = Gl.GL_DEPTH_BUFFER_BIT;

    public static void Clear(int flags) {
        Gl.glClear(flags);
    }

    public static int TRIANGLES = Gl.GL_TRIANGLES;
    public static int TRIANGLE_STRIP = Gl.GL_TRIANGLE_STRIP;
    public static int QUADS = Gl.GL_QUADS;

    public static void Begin(int type) {
        Gl.glBegin(type);
    }

    public static void End() {
        Gl.glEnd();
    }

    public static void Vertex3f(float x, float y, float z) {
        Gl.glVertex3f(x, y, z);
    }

    public static void Color3f(float r, float g, float b) {
        Gl.glColor3f(r, g, b);
    }


    public static void Viewport(int x, int y, int w, int h) {
        Gl.glViewport(x, y, w, h);
    }

    public static int PROJECTION = Gl.GL_PROJECTION;
    public static int MODELVIEW = Gl.GL_MODELVIEW;

    public static void MatrixMode(int m) {
        Gl.glMatrixMode(m);
    }

    public static void LoadIdentity() {
        Gl.glLoadIdentity();
    }

    public static void Rotatef(float x, float y, float z, float w) {
        Gl.glRotatef(x, y, z, w);
    }

    public static void Rotatef(float x, float y, float z) {
        Gl.glRotatef(x, y, z, 0);
    }

    public static void Translatef(float x, float y, float z) {
        Gl.glTranslatef(x, y, z);
    }

    public static void ClearDepth(float f) {
        Gl.glClearDepth(f);
    }

    public static void ClearColor(float r, float g, float b, float a) {
        Gl.glClearColor(r, g, b, a);
    }

    public static int DEPTH_TEST = Gl.GL_DEPTH_TEST;
    public static int LEQUAL = Gl.GL_LEQUAL;

    public static void Enable(int i) {
        Gl.glEnable(i);
    }

    public static void Disable(int i) {
        Gl.glDisable(i);
    }

    public static void DepthFunc(int i) {
        Gl.glDepthFunc(i);
    }
}

public sealed class GLU {
    private GLU() { }

    public static void Perspective(float a, float b, float c, float d) {
        Glu.gluPerspective(a, b, c, d);
    }
}
