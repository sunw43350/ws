import pickle


exchange_symbols = pickle.load(open('assets/exchange_symbols.pkl', 'rb'))
symbol_exchanges = pickle.load(open('assets/symbol_exchanges.pkl', 'rb'))


for ex, syms in sorted(exchange_symbols.items(), key=lambda x: len(x[1])):
    print(ex, len(syms))
