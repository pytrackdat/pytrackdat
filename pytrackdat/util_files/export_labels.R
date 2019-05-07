#!/usr/bin/env Rscript

# PyTrackDat is a utility for assisting in online database creation.
# Copyright (C) 2018-2019 the PyTrackDat authors.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Contact information:
#     David Lougheed (david.lougheed@gmail.com)

chooseCRANmirror(ind=1)

if (!require(baRcodeR)) {
    install.packages("baRcodeR")
    library(baRcodeR)
}

id_vector <- commandArgs(trailingOnly=TRUE)
file_name <- paste("labels-", gsub("[ :]+", "-", Sys.time()), sep="")
create_PDF(Labels=id_vector, name=file.path(getwd(), file_name), Fsz=8)
cat(file_name)
