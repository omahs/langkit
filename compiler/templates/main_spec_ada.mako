## vim: filetype=makoada

with Ada.Containers.Hashed_Maps;
with Ada.Containers.Vectors;
with Ada.Strings.Unbounded; use Ada.Strings.Unbounded;
with Ada.Strings.Unbounded.Hash;

with Interfaces; use Interfaces;

with GNATCOLL.Symbols; use GNATCOLL.Symbols;

with Liblang_Support.AST;                use Liblang_Support.AST;
with Liblang_Support.AST.List;
with Liblang_Support.Diagnostics;        use Liblang_Support.Diagnostics;
with Liblang_Support.Tokens;             use Liblang_Support.Tokens;
with Liblang_Support.Token_Data_Handler; use Liblang_Support.Token_Data_Handler;

package ${_self.ada_api_settings.lib_name} is

   ----------------------
   -- Analysis context --
   ----------------------

   type Analysis_Context_Type;
   type Analysis_Unit_Type;

   type Analysis_Context is access all Analysis_Context_Type;
   type Analysis_Unit is access all Analysis_Unit_Type;

   package Units_Maps is new Ada.Containers.Hashed_Maps
     (Key_Type        => Unbounded_String,
      Element_Type    => Analysis_Unit,
      Hash            => Ada.Strings.Unbounded.Hash,
      Equivalent_Keys => "=");

   type Analysis_Context_Type is record
      Units_Map : Units_Maps.Map;
      Symbols   : Symbol_Table_Access;
   end record;

   type Analysis_Unit_Type is record
      Context     : Analysis_Context;
      Ref_Count   : Natural;
      AST_Root    : AST_Node;
      File_Name   : Unbounded_String;
      TDH         : aliased Token_Data_Handler;
      Diagnostics : Diagnostics_Vectors.Vector;
   end record;

   function Create return Analysis_Context;
   --  Create a new Analysis_Context. When done with it, invoke Destroy on it.

   function Create_From_File
     (Context   : Analysis_Context;
      File_Name : String) return Analysis_Unit;
    --  Create a new Analysis_Unit for "file_name", register it and return a
    --  new reference to it: the caller must decrease the ref count once done
    --  with it.

   procedure Remove (Context   : Analysis_Context;
                     File_Name : String);
   --  Remove the corresponding Analysis_Unit from this context.  If someone
   --  still owns a reference to it, it remains available but becomes
   --  context-less.

   procedure Destroy (Context : in out Analysis_Context);
   --  Invoke Remove on all the units Context contains and free Context

   procedure Inc_Ref (Unit : Analysis_Unit);
   procedure Dec_Ref (Unit : Analysis_Unit);

   procedure Print (Unit : Analysis_Unit);
   --  Debug helper: output the AST and eventual diagnostic for this unit on
   --  standard output

   -----------------------
   -- Enumeration types --
   -----------------------

   ## Output constants so that all concrete AST_Node subclasses get their own
   ## AST_Node_Kind. Nothing can be an instance of an abstract subclass, so
   ## these do not need their own kind. Note that we start from 2 because 1 is
   ## reserved for all lists.
   List_Kind : constant AST_Node_Kind := 1;
   % for cls in _self.astnode_types:
      % if not cls.abstract:
         ${cls.name()}_Kind : constant AST_Node_Kind :=
            ${compile_ctx.node_kind_constants[cls]};
      % endif
   % endfor

   function Image (Value : Boolean) return String is
     (if Value then "True" else "False");

   % for decl in _self.enum_declarations:
   ${decl.public_part}
   % endfor

   ---------------------------
   -- ASTNode derived types --
   ---------------------------

   % for decl in _self.types_declarations:
   ${decl.public_part}
   % endfor

private

   % for decl in _self.types_declarations:
   ${decl.private_part}
   % endfor

end ${_self.ada_api_settings.lib_name};
