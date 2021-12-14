with Langkit_Support.Adalog.Main_Support;
use Langkit_Support.Adalog.Main_Support;

--  Test stateless predicate constructor

procedure Main is
   use T_Solver, Refs, Solver_Ifc;

   function Is_Odd (X : Integer) return Boolean is (X mod 2 = 1);
   function Double (X : Integer) return Integer is (X * 2);
   function Is_Eq (L, R : Integer) return Boolean is (abs L = abs R);

   X : constant Raw_Var := Create ("x");
   Y : constant Raw_Var := Create ("y");
   R : constant Relation :=
     Domain (X, (1, 2, 3, 4, 5, 6))
     and Propagate (X, Y, Converter (Double'Access, "double"))
     and Predicate (X, Predicate (Is_Odd'Access, "is_odd"));

   R2 : constant Relation :=
     Propagate (X, Y, Eq => Comparer (Is_Eq'Access, "is_eq"))
     and Domain (X, (1, 2, 3, 4, 5, 6))
     and Domain (Y, (-1, -2, -3, -4, -5, -6))
     and Predicate (X, Predicate (Is_Odd'Access, "is_odd"));
begin
   Solve_All (R);
   Solve_All (R2);
end Main;
