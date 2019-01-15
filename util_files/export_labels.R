#!/usr/bin/env Rscript

chooseCRANmirror(ind=1)

if (!require(baRcodeR)) {
    install.packages("baRcodeR")
    library(baRcodeR)
}

id_vector <- commandArgs(trailingOnly=TRUE)
file_name <- paste("labels-", gsub("[ :]+", "-", Sys.time()), sep="")
create_PDF(Labels=id_vector, name=file.path(getwd(), file_name), Fsz=8)
cat(file_name)
