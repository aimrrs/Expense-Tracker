document.addEventListener('DOMContentLoaded', function() {

    let selectedMonth = new Date().getMonth() + 1; // Default to the current month (1-based)
    let selectedYear = new Date().getFullYear();

    const addExpenseBtn = document.getElementById('add-expense-btn');
    const expenseModal = document.getElementById('expense-modal');
    const closeModalBtns = document.querySelectorAll('.close-modal');
    const budgetModal = document.getElementById('budget-modal');
    const currentMonthEl = document.getElementById('current-month');
    const monthlyBudgetEl = document.getElementById('monthly-budget');
    const spentAmountEl = document.getElementById('spent-amount');
    const remainingAmountEl = document.getElementById('remaining-amount');

    addExpenseBtn.addEventListener('click', openExpenseModal);
    addExpenseBtn.addEventListener('click', openExpenseModal);

    // Month Selector Elements
    const currentYearEl = document.getElementById('current-year');
    const prevYearBtn = document.getElementById('prev-year');
    const nextYearBtn = document.getElementById('next-year');
    const monthBtns = document.querySelectorAll('.month-btn');
    const dateSelector = document.getElementById('date-selector');
    const monthModal = document.getElementById('month-modal');

    const transactionsListEl = document.getElementById('transactions-list');

    async function loadTransactions() {
        try {
            // Format the month for API request
            let monthStr = selectedMonth.toString().padStart(2, '0');
            let tableName = `m${monthStr}_${selectedYear}`;
            
            // Fetch transactions
            const response = await fetch(`/api/transactions?month=${tableName}`);
            if (response.ok) {
                const data = await response.json();
                
                if (data.success && data.transactions && data.transactions.length > 0) {
                    displayTransactions(data.transactions);
                } else {
                    transactionsListEl.innerHTML = '<tr><td colspan="6" class="text-center">No transactions found</td></tr>';
                }
            }
        } catch (error) {
            console.error('Error loading transactions:', error);
            transactionsListEl.innerHTML = '<tr><td colspan="6" class="text-center">Error loading transactions</td></tr>';
        }
    }

    function displayTransactions(transactions) {
        transactionsListEl.innerHTML = '';
        
        transactions.forEach(transaction => {
            const row = document.createElement('tr');
            
            // Format date
            const date = new Date(transaction.edate);
            const formattedDate = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
            
            row.innerHTML = `
                <td>${transaction.ename}</td>
                <td>${formatCurrency(transaction.amount)}</td>
                <td>${transaction.category}</td>
                <td>${formattedDate}</td>
                <td>${transaction.description || 'N/A'}</td>
                <td>
                    <button class="action-btn edit-btn" data-id="${transaction.id}"><i class="fas fa-edit"></i></button>
                    <button class="action-btn delete-btn" data-id="${transaction.id}"><i class="fas fa-trash"></i></button>
                </td>
            `;
            
            transactionsListEl.appendChild(row);
        });
        
        // Add event listeners for edit and delete buttons
        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.dataset.id;
                // Implement edit functionality
                alert('Edit functionality to be implemented');
            });
        });
        
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.dataset.id;
                if (confirm('Are you sure you want to delete this expense?')) {
                    deleteExpense(id);
                }
            });
        });
    }

    // Open Month Selector Modal
    dateSelector.addEventListener('click', () => {
        // Ensure currentYearEl displays the correct year
        currentYearEl.textContent = selectedYear;

        // Highlight the currently selected month
        monthBtns.forEach(btn => {
            btn.classList.remove('active');
            if (parseInt(btn.dataset.month) === selectedMonth) {
                btn.classList.add('active');
            }
        });

        // Display the month selector modal
        monthModal.style.display = 'flex';
    });

    // Close Modal
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', () => monthModal.style.display = 'none');
    });
    window.addEventListener('click', e => {
        if (e.target === monthModal) monthModal.style.display = 'none';
    });

    // Navigate Between Years
    prevYearBtn.addEventListener('click', () => {
        selectedYear -= 1; // Decrement the selected year
        currentYearEl.textContent = selectedYear;
    });

    nextYearBtn.addEventListener('click', () => {
        selectedYear += 1; // Increment the selected year
        currentYearEl.textContent = selectedYear;
    });

    // Select Month
    monthBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const month = parseInt(btn.dataset.month);
            const year = parseInt(currentYearEl.textContent);
            selectMonth(month, year);
            monthModal.style.display = 'none';
        });
    });

    // Update Selected Month and Year
    function selectMonth(month, year) {
        selectedMonth = month;
        selectedYear = year;
        updateMonthDisplay();
        loadDashboardData();
    }

    // Update Month Display
    function updateMonthDisplay() {
        const monthNames = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
        currentMonthEl.textContent = `${monthNames[selectedMonth - 1]} ${selectedYear}`;
    }

    // For expense btn
    function openExpenseModal() {
        // Set default date to today if not already set
        if (!document.getElementById('expense-date').value) {
            document.getElementById('expense-date').valueAsDate = new Date();
        }
        expenseModal.style.display = 'flex';
    }

    //To close expense btn
    closeModalBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            expenseModal.style.display = 'none';
            monthModal.style.display = 'none';
            budgetModal.style.display = 'none';
        });
    });

    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === expenseModal) {
            expenseModal.style.display = 'none';
        }
        if (e.target === monthModal) {
            monthModal.style.display = 'none';
        }
        if (e.target === budgetModal) {
            budgetModal.style.display = 'none';
        }
    });

    async function loadDashboardData() {
        try {
            let monthStr = selectedMonth.toString().padStart(2, '0');
            let tableName = `m${monthStr}_${selectedYear}`;
            console.log('Fetching data for table:', tableName);
    
            const response = await fetch(`/api/monthly-data?month=${tableName}`);
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    const totalExpense = data.totalExpense || 0;
                    const budget = data.budget || 1200;
                    const remaining = budget - totalExpense;
    
                    monthlyBudgetEl.textContent = formatCurrency(budget);
                    spentAmountEl.textContent = formatCurrency(totalExpense);
                    remainingAmountEl.textContent = formatCurrency(remaining);
                } else {
                    console.warn('No data available for this month.');
                    resetDashboard();
                }
            } else {
                console.error('Failed to fetch data:', response.status);
                resetDashboard();
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            resetDashboard();
        }
    }

    function resetDashboard() {
        monthlyBudgetEl.textContent = '₹0.00';
        spentAmountEl.textContent = '₹0.00';
        remainingAmountEl.textContent = '₹0.00';
    }

    function formatCurrency(amount) {
        return '₹' + parseFloat(amount).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    }
    loadDashboardData();
    loadTransactions();
});