SIMPLEUI_HOME_INFO = [
    {
        'title': 'Marketplace Analytics',
        'content': [
            {
                'type': 'row',
                'gutter': 16,
                'children': [
                    {
                        'type': 'card',
                        'title': 'Sellers',
                        'content': '<h2 id="sellers-count">0</h2><div>Local Sellers Onboarded</div>',
                        'span': 6
                    },
                    {
                        'type': 'card',
                        'title': 'Buyers',
                        'content': '<h2 id="buyers-count">0</h2><div>Buyers</div>',
                        'span': 6
                    },
                    {
                        'type': 'card',
                        'title': 'Products',
                        'content': '<h2 id="products-count">0</h2><div>Total Products</div>',
                        'span': 6
                    },
                    {
                        'type': 'card',
                        'title': 'Total Sales',
                        'content': '<h2 id="total-sales">₱0</h2><div>Total Sales</div>',
                        'span': 6
                    },
                ]
            },
            {
                'type': 'chart',
                'option': {
                    'title': {'text': 'Orders per Month'},
                    'tooltip': {},
                    'legend': {'data':['Orders']},
                    'xAxis': {'data': []},
                    'yAxis': {},
                    'series': [{
                        'name': 'Orders',
                        'type': 'bar',
                        'data': []
                    }]
                },
                'script': """
                fetch('/admin/admin-analytics-data/')
                  .then(response => response.json())
                  .then(data => {
                    option.xAxis.data = data.months;
                    option.series[0].data = data.order_counts;
                    myChart.setOption(option);
                    document.getElementById('sellers-count').innerText = data.sellers_count;
                    document.getElementById('buyers-count').innerText = data.buyers_count;
                    document.getElementById('products-count').innerText = data.products_count;
                    document.getElementById('total-sales').innerText = '₱' + data.total_sales.toLocaleString();
                    document.getElementById('top-product-name').innerText = data.top_product_name;
                    document.getElementById('top-product-sold').innerText = data.top_product_sold;
                  });
                """
            },
            {
                'type': 'card',
                'title': 'Top Selling Product',
                'content': '<h3 id="top-product-name">N/A</h3><div>Sold: <span id="top-product-sold">0</span></div>',
                'span': 12
            }
        ]
    }
] 