pragma solidity ^0.8.0;
// SPDX-License-Identifier: MIT

contract ExpenseTracker {
    struct Expense {
        string category;
        string description;
        uint256 amount;
        uint256 timestamp;
    }

    Expense[] public expenses;

    function logExpense(string memory category, string memory description, uint256 amount) public {
        expenses.push(Expense(category, description, amount, block.timestamp));
    }

    function getExpense(uint256 index) public view returns (string memory, string memory, uint256, uint256) {
        Expense memory expense = expenses[index];
        return (expense.category, expense.description, expense.amount, expense.timestamp);
    }

    function getExpenseCount() public view returns (uint256) {
        return expenses.length;
    }
}
