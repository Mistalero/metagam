#!/bin/sh

# This file is a part of Metagam project.
#
# Metagam is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
# 
# Metagam is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Metagam.  If not, see <http://www.gnu.org/licenses/>.

dir=$(dirname $(dirname $(realpath "$0")))
cd $dir

export LC_CTYPE=ru_RU.UTF-8
export HOME=/home/metagam
export PYTHONPATH=$dir

while true ; do
	screen -D -m -S mmoconstructor bin/mg_procman
done
