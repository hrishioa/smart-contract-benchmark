## Benchmark Suite



### Collated Info

* Read Paper
* Other Benchmark Suites
* Brief Contracts
* Identify Important Features and Properties
    * Most Common Contracts
        * Bytecode
        * ABI
        * Source
    * Formats in Use
        * ERC22
    * Popular Contracts
        * No. of Transactions
        * Ether Held
        * Ether Transacted
        * Popular pieces of Source
    * Examples of Bugs
    * Known contract templates
* Filter Design
* Analysis Parameters
* Run Benchmark
* Package



### 1. BetOnHashV81

* Lottery
* Multiple Rounds
* Bet on last players blockhash (50% probability)
* 6 Players per round
* No payout for loss
* Extra payments per round are refunded
* Payout for win - (winner_pool / winners) - 1%
* Payout triggered when next round starts
* Owner can force a round to end

### 2. BetOnHashV82

* V81 with lower bet amount (10 finney)

### 3. BetOnHashV84

* V81 with lower amount and no forcefinish function

### 4. Big

* ​