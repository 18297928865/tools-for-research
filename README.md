# tools-for-research
  ## DATA SMOOTHING
here we present a tool to smooth your data point by **moving average**
![](https://github.com/18297928865/tools-for-research/blob/main/smooth/f1.png)<br>
click smooth.exe and the UI is like this, here we can see
>**input file:** It must be in .tsv or .txt format, **Tab Delimited File**
>
>**interval length for moving average:** default number is 5. We recommend odd, and if an even is entered, it will +1
>
>**row/line ignored:** there may be tag information about group/time/treatment in the first few rows/lines in your file. Never mind, just ignore them. **There shouldn`t be any tag info at the last few rows/lines in your file**
>
>**placeholder for missing value:** If the length of missing value is longer than that of the interval, the tool will output " "\(space\). Also, you can choose any character you like

The output will be named "input_analysis"
