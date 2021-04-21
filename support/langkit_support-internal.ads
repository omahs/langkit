------------------------------------------------------------------------------
--                                                                          --
--                                 Langkit                                  --
--                                                                          --
--                     Copyright (C) 2014-2021, AdaCore                     --
--                                                                          --
-- Langkit is free software; you can redistribute it and/or modify it under --
-- terms of the  GNU General Public License  as published by the Free Soft- --
-- ware Foundation;  either version 3,  or (at your option)  any later ver- --
-- sion.   This software  is distributed in the hope that it will be useful --
-- but WITHOUT ANY WARRANTY;  without even the implied warranty of MERCHAN- --
-- TABILITY  or  FITNESS  FOR A PARTICULAR PURPOSE.                         --
--                                                                          --
-- As a special  exception  under  Section 7  of  GPL  version 3,  you are  --
-- granted additional  permissions described in the  GCC  Runtime  Library  --
-- Exception, version 3.1, as published by the Free Software Foundation.    --
--                                                                          --
-- You should have received a copy of the GNU General Public License and a  --
-- copy of the GCC Runtime Library Exception along with this program;  see  --
-- the files COPYING3 and COPYING.RUNTIME respectively.  If not, see        --
-- <http://www.gnu.org/licenses/>.                                          --
------------------------------------------------------------------------------

with Langkit_Support.Generic_API; use Langkit_Support.Generic_API;
with Langkit_Support.Text;        use Langkit_Support.Text;

--  This package and its children provide common implementation details for
--  Langkit-generated libraries. Even though it is not private (to allow
--  Langkit-generated libraries to use it), it is not meant to be used beyond
--  this. As such, this API is considered unsafe and unstable.

package Langkit_Support.Internal is

   type Text_Access is not null access constant Text_Type;
   --  Reference to a static Unicode string. Used in descriptor tables whenever
   --  we need to provide a name.

   --  Descriptors for grammar rules

   type Grammar_Rule_Name_Array is
     array (Grammar_Rule_Index range <>) of Text_Access;
   type Grammar_Rule_Name_Array_Access is
     not null access constant Grammar_Rule_Name_Array;

end Langkit_Support.Internal;
