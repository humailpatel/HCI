def initialize():
    paymentCredential = "AMEX: £100"
    return paymentCredential

def checkPaymentProcessor(paymentCredential):
    if (paymentCredential.split()[0] == "AMEX"):
        processAmex(paymentCredential)
    else:
        processVisa(paymentCredential)

def processAmex(paymentCredential):
    paymentCredential = paymentCredential + "0"
    return paymentCredential

def processVisa(paymentCredential):
    paymentCredential = paymentCredential + "0"
    return paymentCredential

def main():
    paymentCredential = initialize()
    checkPaymentProcessor(paymentCredential)

if __name__ == "__main__":
    main()