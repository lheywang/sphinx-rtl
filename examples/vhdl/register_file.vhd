-- Define the register file logic.
--
-- Use a synchronous write logic and an asynchronous read, to enable single cycles operations.
-- Any register except the first (zero) can be wrote.

LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.numeric_std.ALL;

 -- 
ENTITY register_file IS
    GENERIC (
        XLEN : INTEGER := 32; --   Configure the data width in the core.
        REG_NB : INTEGER := 32 --   Configure the number of registers available. May be changed accordingly to configure for example the reduced instruction set.
    );
    PORT (
        --------------------------------------------------------------------------------------------------------
        -- Clocks & controls
        -------------------------------------------------------------------------------------------------------- 
        clock : IN STD_LOGIC; --   clock input of the core. Must match the INPUT_FREQ generics within some tolerance.
        clock_en : IN STD_LOGIC; --   clock enable from the core clock controller. Used to not create two clock domains from the master clock and the auxilliary clock.
        nRST : IN STD_LOGIC; --   reset input, active low. When held to '0', the system will remain in the reset state until set to '1'.

        --------------------------------------------------------------------------------------------------------
        -- Writing port
        --------------------------------------------------------------------------------------------------------
        we : IN STD_LOGIC; --   Write enable pin. Active high. Set to '1' to enable any write operation on the register file.
        wa : IN INTEGER RANGE 0 TO REG_NB - 1;  --   Write address, as an integer.
        wd : IN STD_LOGIC_VECTOR(XLEN - 1 DOWNTO 0);--   Write data, expressed as a vector of the same length as the the default value.

        --------------------------------------------------------------------------------------------------------
        -- Reading ports
        --------------------------------------------------------------------------------------------------------
        ra1 : IN INTEGER RANGE 0 TO REG_NB - 1;  --   Address for the first read port
        rd1 : OUT STD_LOGIC_VECTOR(XLEN - 1 DOWNTO 0);  --   Data for the first read port
        ra2 : IN INTEGER RANGE 0 TO REG_NB - 1; --   Address for the second read port
        rd2 : OUT STD_LOGIC_VECTOR(XLEN - 1 DOWNTO 0)  --   Data for the second read port
    );
END ENTITY;

ARCHITECTURE rtl OF register_file IS
  
    TYPE reg_array_t IS ARRAY (0 TO REG_NB - 1) OF STD_LOGIC_VECTOR(XLEN - 1 DOWNTO 0); --   Type definiton of the register array
    SIGNAL reg_array : reg_array_t := (OTHERS => (OTHERS => '0')); --   instantiation of the register array, to be used.

BEGIN

    --========================================================================================
     --   P1 handle all of the write parts (since reading are done asynchronously).
     -- @details
     -- On each authorized rising edges, if we need to write (WE = '1') and the write
     -- address is not 0 (as per the spec, this register could not be written), 
     -- update the register file.
     -- On reset, the register file is initialized to 0x00000000 for all registers.
    --========================================================================================
    P1 : PROCESS (clock, nRST)
    BEGIN
        IF nRST = '0' THEN
            reg_array <= (OTHERS => (OTHERS => '0'));
        ELSIF rising_edge(clock) AND (clock_en = '1') THEN
            IF (we = '1') AND (wa /= 0) THEN
                reg_array(wa) <= wd;
            END IF;
        END IF;
    END PROCESS;

    -- asynchronous reads (combinational muxes)
    rd1 <= (OTHERS => '0') WHEN ra1 = 0 ELSE
        reg_array(ra1);
    rd2 <= (OTHERS => '0') WHEN ra2 = 0 ELSE
        reg_array(ra2);

END ARCHITECTURE;