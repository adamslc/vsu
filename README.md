# VSim Utility

This is a tool to make VSim text-based setup better and easier.
To use this, you should export an enviroment variable called VSC_PATH that
points to the directory that contains VSimComposer.sh. On MacOS, this will look
something like:
/Applications/VSim-11.0/VSimComposer.app/Contents/Resources/
Then invoke any command, and it will ask you for the basename of your .sdf or
.pre file.

This should be used in a directory that VSimComposer is not being used in. I
like to create a subdirectory called vsim, and move all of the VSimComposer
generated files into there. Then I symlink <basename>.sdf into the parent
directory, and use vsu from there.

Possible commands:
1. make: creates the .in file from the .sdf or .pre basefile. You can optionally
   include a set of variable substitutions to be applied during the creation of
   the .in file. These variables should be of the form 'var1=value1 var2=value2'
   *including the quotes*.
2. run: run the simulation using the generated .in file. This will fail if make
   hasn't been run first. By default, the output files will be written to the
   subdirectory data. This command also accepts variable substitutions; see
   make.
3. params: show the variable substitutions that were made to generate the .in
   file.
4. clean: remove all of the generated files.
5. update: create or update the .patch files
6. history: supposed to create a nice overview of the histories. Only kind of
   works right now.
