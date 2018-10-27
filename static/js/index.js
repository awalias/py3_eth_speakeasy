var eth_address;

$( document ).ready(function() {
    $('.goldbutt').click(function(){
        eth_verify();
    });
});

var eth_verify = async() => {
    // Modern dapp browsers...
    if (window.ethereum) {
        window.web3 = new Web3(ethereum);
        try {
            // Request account access if needed
            await ethereum.enable();
            // Acccounts now exposed
            attempt_auth();
        } catch (error) {
            // User denied account access...
            $('.popper').show();
        }
    }
    // Legacy dapp browsers...
    else if (window.web3) {
        window.web3 = new Web3(web3.currentProvider);
        // Acccounts always exposed
        attempt_auth();
    }
    // Non-dapp browsers...
    else {
        alert('Non-Ethereum browser detected. You should consider trying MetaMask!');
    }
}

var attempt_auth = async() => {
    web3.eth.getAccounts(function(e,accounts){
      var balance = 0;
      web3.eth.getBalance(accounts[0], "latest", function(a,b) {
        eth_address = web3.toChecksumAddress(accounts[0]);
        balance = b.toNumber();
        get_nonce(balance, web3.toChecksumAddress(accounts[0]));
      })
    });
}

var get_nonce = async(balance, eth_address) => {
    $.ajax({
      type: "POST",
      url: "/auth",
      data: {
        'step' : 'init',
        'eth_address' : eth_address
      },
      success: submit_signature,
      dataType: "json",
    });
}

var submit_signature = async(data) => {
  web3.personal.sign(
    web3.fromUtf8('ETH Speakeasy Login code: ' + data.nonce),
    eth_address,
    (err, signature) => {
      if (err) $('.popper').show();
      $.ajax({
        type: "POST",
        url: "/auth",
        data: {
          'step' : 'auth',
          'signed_nonce' : signature,
          'eth_address' : eth_address,
        },
        dataType: "json",
      })
      .done(function(data) {
        if (data['success']) {
          var newDoc = document.open("text/html");
          newDoc.write(data['message']);
          newDoc.close();
        } else {
          $('.popper').show();
        }
      })
      .fail(function(data) {
        $('.popper').show();
      })
    }
  )
  console.log(data);
}
