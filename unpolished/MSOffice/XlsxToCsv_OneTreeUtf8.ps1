# This script converts every *.xlsx file in the folders below .\xlsx\*
# into CSV files in an identical folder structure below .\csv\*

# References:
#   Initial Excel boilerplate:
#   https://zeleskitech.com/2014/10/26/convert-xlsx-csv-powershell/
#   UTF-8 Conversion:
#   http://www.powershelladmin.com/wiki/Convert_from_most_encodings_to_utf8_with_powershell
#   Getting Excell to close cleanly:
#   http://stackoverflow.com/questions/38504265/close-excel-application-using-powershell
#   Enums in Powershell  (so I didn't have to hard-code _6_ for CSV format):
#   https://blogs.technet.microsoft.com/heyscriptingguy/2015/08/27/working-with-enums-in-powershell-5/
#   Create directory if not exists
#   http://stackoverflow.com/questions/16906170/create-directory-if-it-does-not-exist

Add-Type -AssemblyName Microsoft.Office.Interop.Excel

Get-ChildItem -Filter *.xlsx -Recurse | ForEach{
    # Pass the relative paths to the next block
    $_.FullName.substring((pwd).Path.length+1) 
} | ForEach{
    # Change the file extension
    $csvFilePath = $_.substring(0, $_.length-5)+".localCP.csv"
    $csvFilePathUtf8 = $_.substring(0, $_.length-5)+".csv"
    # Extract the relative path
    $csvPath = Split-Path -Parent $csvFilePath 
    # COM Object needs the full path ... add the current directory back in
    $csvFilePath = (pwd).Path+"\"+$csvFilePath
    # Load up a hidden Excel engine
    $Excel = New-Object -ComObject Excel.Application
    $Excel.Visible = $false
    $Excel.DisplayAlerts = $false
    
    $wb = $Excel.Workbooks.Open((pwd).Path+"\"+$_)
    $ws = $wb.Worksheets.Item(1)
    $ws.SaveAs($csvFilePath, [Microsoft.Office.Interop.Excel.XlFileFormat]::xlCSV)
    # Convert local CodePage 1252 CSV to UTF-8 CSV:
    Get-Content $csvFilePath | Set-Content -Encoding utf8 $csvFilePathUtf8
    
    $Excel.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($Excel)
    Remove-Variable Excel    
    
    $csvFilePathUtf8
    [Console]::Out.Flush()

    Remove-Item $csvFilePath
}


