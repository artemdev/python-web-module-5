

const ws = new WebSocket('ws://localhost:8080')

formChat.addEventListener('submit', (e) => {
    e.preventDefault()
    ws.send(textField.value)
})

ws.onopen = (e) => {
    console.log('Hello WebSocket!')
}

ws.onmessage = (e) => {
    parsedData = JSON.parse(e.data)
    const tbody = document.querySelector('tbody');

    tbody.innerHTML = '';
    if (parsedData.loading === 'true') {
        tbody.innerHTML = 'Loading ...'
    }

    if (parsedData.rates.length > 0) {
        tbody.innerHTML = ''
        parsedData.rates.forEach((date) => {
        const parsedDate = JSON.parse(date)

        parsedDate.exchangeRate.forEach(rate => {
            const row = document.createElement('tr');
            row.innerHTML = `
            <td>${parsedDate.date}</td>
            <td>${rate.currency}</td>
            <td>${rate.saleRateNB}</td>
            <td>${rate.purchaseRateNB}</td>
            <td>${rate.saleRate || ''}</td>
            <td>${rate.purchaseRate || ''}</td>
        `;
            tbody.appendChild(row)
        })
        });
    }
}