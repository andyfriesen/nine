using System;

//used to generate ClassLibrary1.dll

namespace TestClass {
	/// <summary>
	/// Summary description for Class1.
	/// </summary>
	public class TestClass    {
		public class NestedClass {
			public NestedClass() {
				Console.WriteLine("TestClass.NestedClass()");
			}
		}

		public TestClass() {
			Console.WriteLine("TestClass()");
		}

		public TestClass(int x) {
			Console.WriteLine("TestClass({0})", x);
		}

		public TestClass(string s) {
			Console.WriteLine("TestClass(\"{0}\")", s);
		}

		public void Method(string s) {
			Console.WriteLine("TestClass.Method(string \"{0}\")", s);
		}

		public void Method(int i) {
			Console.WriteLine("TestClass.Method(int {0})", i);
		}

		public static void StaticMethod(string s) {
			Console.WriteLine("TestClass.StaticMethod(string \"{0}\")", s);
		}

		public static void StaticMethod(int i) {
			Console.WriteLine("TestClass.StaticMethod(int {0})", i);
		}

		public int x;
		public string y;

		public static int s;

		public string Property {
			get {
				return "Property! " + y;
			}

			set {
				y = value;
			}
		}

		public static int StaticProperty {
			get {
				return s;
			}
			set {
				s = value;
			}
		}
	}

	public class UnaryOperators {
		public static UnaryOperators operator + (UnaryOperators arg) { return arg; }
		public static UnaryOperators operator - (UnaryOperators arg) { return arg; }
		public static UnaryOperators operator ! (UnaryOperators arg) { return arg; }
		public static UnaryOperators operator ~ (UnaryOperators arg) { return arg; }
		public static UnaryOperators operator ++ (UnaryOperators arg) { return arg; }
		public static UnaryOperators operator -- (UnaryOperators arg) { return arg; }
		public static bool operator true (UnaryOperators arg) { return true; }
		public static bool operator false(UnaryOperators arg) { return false; }
	}

	public class BinaryOperators {
		public static BinaryOperators operator + (BinaryOperators lhs, BinaryOperators rhs) { return lhs; }
		public static BinaryOperators operator - (BinaryOperators lhs, BinaryOperators rhs) { return lhs; }
		public static BinaryOperators operator * (BinaryOperators lhs, BinaryOperators rhs) { return lhs; }
		public static BinaryOperators operator / (BinaryOperators lhs, BinaryOperators rhs) { return lhs; }
		public static BinaryOperators operator % (BinaryOperators lhs, BinaryOperators rhs) { return lhs; }
		public static BinaryOperators operator & (BinaryOperators lhs, BinaryOperators rhs) { return lhs; }
		public static BinaryOperators operator | (BinaryOperators lhs, BinaryOperators rhs) { return lhs; }
		public static BinaryOperators operator ^ (BinaryOperators lhs, BinaryOperators rhs) { return lhs; }
		public static BinaryOperators operator << (BinaryOperators lhs, int rhs) { return lhs; }
		public static BinaryOperators operator >> (BinaryOperators lhs, int rhs) { return lhs; }
		public static BinaryOperators operator == (BinaryOperators lhs, BinaryOperators rhs) { return lhs; }
		public static BinaryOperators operator != (BinaryOperators lhs, BinaryOperators rhs) { return lhs; }
		public static BinaryOperators operator > (BinaryOperators lhs, BinaryOperators rhs) { return lhs; }
		public static BinaryOperators operator < (BinaryOperators lhs, BinaryOperators rhs) { return lhs; }
		public static BinaryOperators operator >= (BinaryOperators lhs, BinaryOperators rhs) { return lhs; }
		public static BinaryOperators operator <= (BinaryOperators lhs, BinaryOperators rhs) { return lhs; }
	}

	public class ConversionOperators {
		public static explicit operator int(ConversionOperators arg) { return 0; }
		public static explicit operator float(ConversionOperators arg) { return 0; }
		public static implicit operator string(ConversionOperators arg) { return arg.ToString(); }
		public static implicit operator byte(ConversionOperators arg) { return 0; }
	}

	public class Indexer {
		public int this[int i, int j, int k] {
			get { return 0; }
			set { }
		}
	}

	public class MultidimArray {
		public static float[,] a;
		static MultidimArray() {
			a = new float[22, 23];
		}

		static void Get() {
			Console.WriteLine(a[10,11]);
		}

		static void Set() {
			a[2, 3] = 44.4f;
		}
	}

	public sealed class SealedClass {
		public SealedClass() {
			Console.WriteLine("SealedClass");
		}
	}
}
