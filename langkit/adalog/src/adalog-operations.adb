------------------------------------------------------------------------------
--                               A D A L O G                                --
--                                                                          --
--                     Copyright (C) 2016, AdaCore                          --
--                                                                          --
-- This library is free software;  you can redistribute it and/or modify it --
-- under terms of the  GNU General Public License  as published by the Free --
-- Software  Foundation;  either version 3,  or (at your  option) any later --
-- version. This library is distributed in the hope that it will be useful, --
-- but WITHOUT ANY WARRANTY;  without even the implied warranty of MERCHAN- --
-- TABILITY or FITNESS FOR A PARTICULAR PURPOSE.                            --
--                                                                          --
-- As a special exception under Section 7 of GPL version 3, you are granted --
-- additional permissions described in the GCC Runtime Library Exception,   --
-- version 3.1, as published by the Free Software Foundation.               --
--                                                                          --
-- You should have received a copy of the GNU General Public License and    --
-- a copy of the GCC Runtime Library Exception along with this program;     --
-- see the files COPYING3 and COPYING.RUNTIME respectively.  If not, see    --
-- <http://www.gnu.org/licenses/>.                                          --
--                                                                          --
------------------------------------------------------------------------------

package body Adalog.Operations is

   ----------
   -- Call --
   ----------

   function Solve (Inst : in out Or_Rec) return Boolean is
   begin
      case Inst.State is
         when 0 => null;
         when 1 => goto State_1;
         when others => goto State_2;
      end case;

      if Inst.Left.Solve then
         return True;
      end if;

      <<State_1>>
      Inst.State := 1;
      if Inst.Right.Solve then
         return True;
      end if;

      <<State_2>>
      Inst.State := 2;
      return False;
   end Solve;

   -----------
   -- Reset --
   -----------

   procedure Reset (Inst : in out Or_Rec) is
   begin
      Inst.State := 0;
      Inst.Left.Reset;
      Inst.Right.Reset;
   end Reset;

   ----------
   -- Call --
   ----------

   function Solve (Inst : in out And_Rec) return Boolean is
   begin
      case Inst.State is
         when 0 => goto State_0;
         when 1 => goto State_1;
         when others => goto State_2;
      end case;

      <<State_0>>
      while Inst.Left.Solve loop
         Inst.State := 1;
         if Inst.Right.Solve then
            return True;
         else
            Inst.Right.Reset;
            Inst.State := 0;
         end if;
      end loop;
      goto State_2;

      <<State_1>>
      Inst.State := 1;
      if Inst.Right.Solve then
         return True;
      else
         Inst.Right.Reset;
         Inst.State := 0;
      end if;
      goto State_0;

      <<State_2>>
      Inst.State := 2;
      return False;
   end Solve;

   -----------
   -- Reset --
   -----------

   procedure Reset (Inst : in out And_Rec) is
   begin
      Inst.State := 0;
      Inst.Left.Reset;
      Inst.Right.Reset;
   end Reset;

   ----------
   -- Free --
   ----------

   procedure Cleanup (Inst : in out And_Rec) is
   begin
      Dec_Ref (Inst.Left);
      Dec_Ref (Inst.Right);
   end Cleanup;

   ----------
   -- Free --
   ----------

   procedure Cleanup (Inst : in out Or_Rec) is
   begin
      Dec_Ref (Inst.Left);
      Dec_Ref (Inst.Right);
   end Cleanup;

   --------------
   -- Logic_Or --
   --------------

   function Logic_Or
     (L, R : Relation) return access I_Relation'Class
   is
      Result : constant access I_Relation'Class :=
         new Or_Rec'(Left => L, Right => R, others => <>);
   begin
      Inc_Ref (L);
      Inc_Ref (R);
      return Result;
   end Logic_Or;

   ---------------
   -- Logic_And --
   ---------------

   function Logic_And
     (L, R : Relation) return access I_Relation'Class
   is
      Result : constant access I_Relation'Class :=
         new And_Rec'(Left => L, Right => R, others => <>);
   begin
      Inc_Ref (L);
      Inc_Ref (R);
      return Result;
   end Logic_And;

end Adalog.Operations;
