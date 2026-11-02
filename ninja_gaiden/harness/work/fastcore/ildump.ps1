param([string]$TypeRegex, [string]$MethodRegex)
$p = "G:\AI World Record\BizHawk-2.11.1-win-x64\dll\BizHawk.Emulation.Cores.dll"
try { $asm = [System.Reflection.Assembly]::LoadFrom($p); $types = $asm.GetTypes() } catch [System.Reflection.ReflectionTypeLoadException] { $types = $_.Exception.Types | Where-Object { $_ -ne $null } }
$one = @{}; $two = @{}
foreach ($f in [System.Reflection.Emit.OpCodes].GetFields()) { $op = $f.GetValue($null); $v = [int]$op.Value -band 0xFFFF; if ($op.Size -eq 1) { $one[$v] = $op } else { $two[$v -band 0xFF] = $op } }
$flags = [System.Reflection.BindingFlags]'Public,NonPublic,Instance,Static,DeclaredOnly'
foreach ($t in $types | Where-Object { $_.FullName -match $TypeRegex }) {
  foreach ($m in $t.GetMethods($flags) + $t.GetConstructors($flags)) {
    if ($m.Name -notmatch $MethodRegex) { continue }
    $body = $m.GetMethodBody(); if (-not $body) { continue }
    $il = $body.GetILAsByteArray(); $mod = $m.Module
    "=== $($t.FullName)::$($m.Name)"
    $i = 0
    while ($i -lt $il.Length) {
      $start = $i; $b = $il[$i]; $i++
      if ($b -eq 0xFE) { $op = $two[[int]$il[$i]]; $i++ } else { $op = $one[[int]$b] }
      $arg = ""
      switch ($op.OperandType.ToString()) {
        "InlineNone" { }
        "ShortInlineBrTarget" { $d = [sbyte]([int]$il[$i] - (([int]$il[$i] -band 0x80) * 2)); $i++; $arg = "IL_{0:X4}" -f ($i + $d) }
        "ShortInlineI" { $arg = [int]$il[$i]; $i++ }
        "ShortInlineVar" { $arg = [int]$il[$i]; $i++ }
        "InlineBrTarget" { $d = [BitConverter]::ToInt32($il, $i); $i += 4; $arg = "IL_{0:X4}" -f ($i + $d) }
        "InlineI" { $arg = [BitConverter]::ToInt32($il, $i); $i += 4 }
        "InlineI8" { $arg = [BitConverter]::ToInt64($il, $i); $i += 8 }
        "ShortInlineR" { $arg = [BitConverter]::ToSingle($il, $i); $i += 4 }
        "InlineR" { $arg = [BitConverter]::ToDouble($il, $i); $i += 8 }
        "InlineVar" { $arg = [BitConverter]::ToInt16($il, $i); $i += 2 }
        "InlineSwitch" { $n = [BitConverter]::ToInt32($il, $i); $i += 4; $base = $i + 4 * $n; $ts = @(); for ($k = 0; $k -lt $n; $k++) { $ts += ("IL_{0:X4}" -f ($base + [BitConverter]::ToInt32($il, $i))); $i += 4 }; $arg = ($ts -join ",") }
        "InlineString" { $tok = [BitConverter]::ToInt32($il, $i); $i += 4; try { $arg = '"' + $mod.ResolveString($tok) + '"' } catch { $arg = "str?" } }
        default { $tok = [BitConverter]::ToInt32($il, $i); $i += 4; try { $mm = $mod.ResolveMember($tok); $arg = "$($mm.DeclaringType.Name)::$($mm.Name)" } catch { $arg = "tok{0:X8}" -f $tok } }
      }
      "IL_{0:X4} {1} {2}" -f $start, $op.Name, $arg
    }
  }
}
