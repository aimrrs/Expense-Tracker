document.addEventListener('DOMContentLoaded', function() {

    let selectedMonth = new Date().getMonth() + 1; // Default to the current month (1-based)
    let selectedYear = new Date().getFullYear();

    const addExpenseBtn = document.getElementById('add-expense-btn');
    const expenseModal = document.getElementById('expense-modal');
    const closeModalBtns = document.querySelectorAll('.close-modal');
    const currentMonthEl = document.getElementById('current-month');
    const spentAmountEl = document.getElementById('spent-amount');
    const expenseForm = document.getElementById('expense-form');

    addExpenseBtn.addEventListener('click', openExpenseModal);
    addExpenseBtn.addEventListener('click', openExpenseModal);

    expenseForm.addEventListener('submit', handleAddExpense);

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
                    <button class="action-btn edit-btn" data-date="${formattedDate}" data-name="${transaction.ename}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn delete-btn" data-date="${formattedDate}" data-name="${transaction.ename}">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            
            transactionsListEl.appendChild(row);
        });
        
        // Add event listeners for edit and delete buttons
        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const date = this.dataset.date;
                const name = this.dataset.name;
                // Implement edit functionality
                alert(`Edit functionality for ${name} on ${date} to be implemented`);
            });
        });
        
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const date = this.dataset.date;
                const name = this.dataset.name;
                if (confirm(`Are you sure you want to delete the expense "${name}" on ${date}?`)) {
                    deleteExpense(date, name);
                }
            });
        });
    }

    async function deleteExpense(date, name) {
        try {
            const response = await fetch('/api/delete-expense', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json', // Set the correct Content-Type
                },
                body: JSON.stringify({ date, name }), // Send data as JSON
            });

            if (response.ok) {
                const data = await response.json();
                console.log('Expense deleted successfully:', data);

                if (data.success) {
                    // Reload transactions and dashboard data
                    await loadTransactions(); // Reload the transactions table
                    await loadDashboardData(); // Optionally reload the dashboard data
                    await loadCardData();
                } else {
                    alert('Error deleting expense: ' + data.message);
                }
            } else {
                console.error('Failed to delete expense:', response.status);
            }
        } catch (error) {
            console.error('Error deleting expense:', error);
        }
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
        loadDashboardData(); // Update the spent amount
        loadTransactions();  // Update the transactions
        loadCardData(month, year); // Update the card data
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
    });

    async function loadUserInfo() {
        try {
            // Fetch user info from the API
            const response = await fetch('/api/user-info');
            if (response.ok) {
                const data = await response.json();
                if (data.success && data.user) {
                    const userName = data.user.name;
                    const userAvatarLetter = userName.charAt(0).toUpperCase();
    
                    // Update the username and avatar
                    document.getElementById('username').textContent = userName;
                    document.getElementById('user-avatar').textContent = userAvatarLetter;
                } else {
                    console.error('Failed to load user info:', data.message);
                }
            } else {
                console.error('Failed to fetch user info:', response.status);
            }
        } catch (error) {
            console.error('Error loading user info:', error);
        }
    }
    
    // Call the function when the page loads
    document.addEventListener('DOMContentLoaded', loadUserInfo);


    async function loadDashboardData() {
        try {
            let monthStr = selectedMonth.toString().padStart(2, '0');
            let tableName = `m${monthStr}_${selectedYear}`;
            console.log('Fetching data for table:', tableName);
    
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            resetDashboard();
        }
    }

    function resetDashboard() {
        spentAmountEl.textContent = '₹0.00';
    }

    function formatCurrency(amount) {
        return '₹' + parseFloat(amount).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    }

    async function handleAddExpense(e) {
        e.preventDefault();
        
        const name = document.getElementById('expense-name').value;
        const amount = document.getElementById('expense-amount').value;
        const category = document.getElementById('expense-category').value;
        const date = document.getElementById('expense-date').value;
        const description = document.getElementById('expense-description').value || 'Null';
        
        try {
            const response = await fetch('/api/add-expense', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    amount: amount,
                    category: category,
                    date: date,
                    description: description
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    // Reset form and close modal
                    expenseForm.reset();
                    expenseModal.style.display = 'none';
                    
                    // Set default date to today
                    document.getElementById('expense-date').valueAsDate = new Date();
                    
                    // Reload dashboard data and transactions
                    await loadDashboardData();
                    await loadTransactions();
                } else {
                    alert('Error adding expense: ' + data.message);
                }
            }
        } catch (error) {
            console.error('Error adding expense:', error);
            alert('Error adding expense');
        }
    }

    async function loadCardData(month, year) {
        try {
            // Fetch card data from the API
            const response = await fetch(`/api/card-data?month=${month}&year=${year}`);
            if (response.ok) {
                const data = await response.json();
                console.log('Card Data API Response:', data); // Debugging log

                if (data.success && data.cardData) {
                    // Update the card data
                    const spentAmountEl = document.getElementById('spent-amount');
                    const noTransactionsEl = document.getElementById('no-transactions');
                    const topCatEl = document.getElementById('top-cat');
                    const topCatAmtEl = document.getElementById('top-cat-amt');

                    if (spentAmountEl) spentAmountEl.textContent = formatCurrency(data.cardData.total_spent);
                    if (noTransactionsEl) noTransactionsEl.textContent = data.cardData.transaction_count || 0;
                    if (topCatEl) topCatEl.textContent = data.cardData.most_spent_category || 'None';
                    if (topCatAmtEl) topCatAmtEl.textContent = formatCurrency(data.cardData.most_spent_amount || 0);
                } else {
                    console.warn('No data available for the selected month.');
                    resetCardData(); // Reset card data to default values
                }
            } else {
                console.error('Failed to fetch card data:', response.status);
                resetCardData(); // Reset card data to default values
            }
        } catch (error) {
            console.error('Error loading card data:', error);
            resetCardData(); // Reset card data to default values
        }
    }

    function resetCardData() {
        document.getElementById('spent-amount').textContent = '₹0.00';
        document.getElementById('no-transactions').textContent = '0';
        document.getElementById('top-cat').textContent = 'None';
        document.getElementById('top-cat-amt').textContent = '₹0.00';
    }

    // Update card data when the month selector changes
    document.getElementById('date-selector').addEventListener('click', () => {
        const activeMonthBtn = document.querySelector('.month-btn.active');
        if (activeMonthBtn) {
            selectedMonth = parseInt(activeMonthBtn.dataset.month);
            selectedYear = parseInt(document.getElementById('current-year').textContent);
            console.log('Selected Month:', selectedMonth);
            console.log('Selected Year:', selectedYear);
            loadCardData(selectedMonth, selectedYear);
        } else {
            console.error('No active month button found.');
        }
    });

    // Call the function on page load
    document.addEventListener('DOMContentLoaded', () => {
        console.log('Initial Month:', selectedMonth);
        console.log('Initial Year:', selectedYear);
        loadCardData(selectedMonth, selectedYear);
    });

    updateMonthDisplay();
    loadCardData();
    loadUserInfo();
    loadTransactions();
});