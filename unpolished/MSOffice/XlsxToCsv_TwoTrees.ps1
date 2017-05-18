# This script converts every *.xlsx file in the folders below .\xlsx\*
# into CSV files in an identical folder structure below .\csv\*

Get-ChildItem -Filter *.xlsx -Recurse xlsx | ForEach{
    # Pass the relative paths to the next block
    $_.FullName.substring((pwd).Path.length+1) 
} | ForEach{
    # Change the file extension
    $csvFilePath = $_.substring(0, $_.length-5)+".csv"
    # Change the child directory from "xlsx" to "csv"
    $csvFilePath = "csv"+$csvFilePath.substring("xlsx".length)
    # Extract the relative path
    $csvPath = Split-Path -Parent $csvFilePath 
    # COM Object needs the full path ... add the current directory back in
    $csvFilePath = (pwd).Path+"\"+$csvFilePath
    # Make sure the target directory exists
    New-Item -ItemType Directory -Force -Path $csvPath
    # Load up a hidden Excel engine
    $Excel = New-Object -ComObject Excel.Application
    $Excel.Visible = $false
    $Excel.DisplayAlerts = $false
    
    $wb = $Excel.Workbooks.Open((pwd).Path+"\"+$_)
    $ws = $wb.Worksheets.Item(1)
    $ws.SaveAs($csvFilePath, [Microsoft.Office.Interop.Excel.XlFileFormat]::xlCSV)
        
    $Excel.Quit()
    $csvFilePath
}


