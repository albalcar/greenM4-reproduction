#Import eco2ai and measure the CO2 footprint
library(reticulate)
Tracker <- import("eco2ai", convert = FALSE)$Tracker
track_id <- Tracker(project_name="Datos_036", experiment_description="Carga_datos_036")
track_id$start()

filenames = c("Yearly", "Quarterly", "Monthly", "Weekly", "Daily", "Hourly")
horizons = c(6, 8, 18, 13, 14, 48)
freqs = c(1, 4, 12, 52, 7, 168)

for (d in 1:6){
  conn <- file(paste0("data/train/", filenames[d], "-train.csv"),open="r")
  linn <- readLines(conn)
  
  series = NULL
  for (i in 2:length(linn)){
    print(paste(d, i))
    
    aline = linn[i]
    aline = strsplit(aline, ",")[[1]]
    n = min(as.numeric(min(which(aline == "")) - 2), length(aline) - 1)
    x = array(NA, n)
    for (i in 1:n){
      x[i] = as.numeric(substr(aline[i+1], 2, nchar(aline[i+1]) - 1))
    }
    
    series = append(series, list(list(n=n, h=horizons[d], frequency=freqs[d], x=ts(x, frequency=freqs[d]))))
  }
  
  close(conn)
  save(series, file=paste0("data/RData/", filenames[d], ".RData"))
}
track_id$stop()
emision <- read.csv("emission.csv")
emision = emision[nrow(emision),]
write.csv(emision, file = "carga_datos_036.cvs")
