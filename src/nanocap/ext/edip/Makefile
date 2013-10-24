
OBJ = checkcell.o\
checkinput.o\
checkrij.o\
conductivity.o\
constants.o\
coordination.o\
cutoff.o\
defaults.o\
density.o\
dihedral.o\
dihedral2.o\
dihedral4.o\
distance.o\
distnab.o\
distribution.o\
edgetherm.o\
energy.o\
force.o\
init.o\
linear.o\
main.o\
makespecial.o\
neighbour.o\
pair.o\
parse.o\
printav.o\
printfinish.o\
printinput.o\
printrings.o\
printstatus.o\
printtime.o\
properties.o\
readcoords.o\
readinput.o\
remspace.o\
repulsion.o\
resetmsd.o\
runspecial.o\
stress.o\
therm.o\
triple.o\
volume.o\
verlet.o\
writecoords.o\
writegr.o\
writestress.o\
writetheta.o\
writexbs.o

GOAL = edip-rcpomp
INCL = common.f
FFLAGS = 
FC = gfortran

$(GOAL): $(OBJ) ; \
	$(FC) $(OBJ) $(FFLAGS) -o $(GOAL)

$(OBJ): $(INCL)

.f.o:; $(FC) $(FFLAGS) -c $<

clean:; rm *.o


