library(ggplot2)
d <- read.csv('sprints.csv', header=TRUE)
df = data.frame(date=as.Date(d$date), points=d$points)
ggplot(df, aes(date, points)) + geom_line()
