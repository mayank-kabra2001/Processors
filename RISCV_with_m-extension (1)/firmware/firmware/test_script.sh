echo "Welcome to Processor"
echo "+++++++++++++++++++++++++++++++++++++++"
echo "Enter benchmarking test :"
read mytest 
echo "+++++++++++++++++++++++++++++++++++++++"

mkdir generated_${mytest}
echo "Compiling your code"
riscv32-unknown-elf-gcc -c -mabi=ilp32 -march=rv32i  -ffreestanding -nostdlib -o ./generated_${mytest}/${mytest} ${mytest}.c
riscv32-unknown-elf-objdump -d generated_${mytest}/${mytest} > generated_${mytest}/${mytest}.txt
echo "Done compiling and generate asssembly"
echo "+++++++++++++++++++++++++++++++++++++++"

echo "Generating binary file"
cd generated_${mytest}
python3 ./../../firmware/cleaner.py ${mytest}
rm ${mytest}_cleaned1.txt
rm ${mytest}_cleaned2.txt
cd ..
echo "Done Generating binary file"
echo "+++++++++++++++++++++++++++++++++++++++"
