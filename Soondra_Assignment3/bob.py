from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory, PNOperationType
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import sys, os
import json
import hashlib #for hashfunction

ledger_count = 1
transactions = [ "[3, 4, 5, 6]", "[4, 5, 6, 7]", "[5, 6, 7, 8]", "[6, 7, 8, 9]", "[7, 8, 9, 10]", "[8, 9, 10, 11]", "[9, 10, 11, 12]", "[10, 11, 12, 13]", "[11, 12, 13, 14]", "[12, 13, 14, 15]", "[13, 14, 15, 16]"]
tx = json.dumps({"Block Number": 0, "Hash": "Genesis", "Transation": "", "Nonce":0}, sort_keys=True, indent=4, separators=(',',': '))

pnconfig = PNConfiguration()

pnconfig.subscribe_key = 'sub-c-c56a6168-b75a-4a97-ac15-0e7f0b660b51'
pnconfig.publish_key = 'pub-c-845945be-2dd1-4da5-87e0-f3afdd49189a'
pnconfig.uuid = 'Bob'
pubnub = PubNub(pnconfig)

#####################################################################################################################################

def verify_block(block):
    global ledger_count
    #verify
    fr = open("ledger" + str(ledger_count - 1) + ".json","r")
    old_block = fr.read()
    fr.close()
    hashval = hashlib.sha256(old_block.encode()).hexdigest()

    new_block = json.loads(str(block))

    if new_block["Hash"] == hashval:
        #to store the created dataset to ledger#.txt
        fw = open("ledger" + str(ledger_count) + ".json","w+")
        b = json.dumps(new_block, sort_keys=True, indent=4, separators=(',',': '))
        fw.write(b)
        fw.close()
        print("Hash valid for block: "+str(ledger_count)+"\n")
        return True
    else:
        return False


def mine():
    global ledger_count
    ledger_count += 1
    if ledger_count > 10:
        os. _exit(0)

    #get hash value of previous block
    fr = open("ledger" + str(ledger_count-1) + ".json","r")
    data = fr.read()
    fr.close()
    prev_hashval = hashlib.sha256(data.encode()).hexdigest()

    #make new block
    block = {"Block Number": ledger_count, "Hash": prev_hashval, "Transaction": transactions[ledger_count-1], "Nonce":1000000000}

    #to store the created dataset to ledger#.txt
    fw = open("ledger" + str(ledger_count) + ".json","w+")
    json.dump(block, fw, sort_keys=True, indent=4, separators=(',',': '))
    fw.close()

    #get current hash value
    fr = open("ledger" + str(ledger_count) + ".json","r")
    data = fr.read()
    fr.close()
    hashval = hashlib.sha256(data.encode()).hexdigest()


    #64 bytes = 256 bit (for sha256), hex represents 4 bits
    #if all 0, then binary 4 bits all 0 -> 4 hex zeros = first 20 bits must be equal to zero
    #SHA256 HASH < 2^236
    while hashval > "00000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffff":
        block["Nonce"] = block["Nonce"]+1
	
        #print("Block:", str(block_number), "\n")		
        #print("Nonce Counter at: "+ str(block["Nonce"]), "\n")
	
        fw = open("ledger" + str(ledger_count) + ".json","w+")
        json.dump(block, fw, sort_keys=True, indent=4, separators=(',',': '))
        fw.close()
		
        fr = open("ledger" + str(ledger_count) + ".json","r")
        data = fr.read()
        fr.close()
        hashval = hashlib.sha256(data.encode()).hexdigest()

    #create json block
    tx = {"Block Number": ledger_count, "Hash": prev_hashval, "Transaction": transactions[ledger_count-1], "Nonce":block["Nonce"]}
    #increment block counter
    ledger_count += 1
    #return string for printing
    return tx


def my_publish_callback(envelope, status):
    # Check whether request successfully completed or not
    if not status.is_error():
        pass  # Message successfully published to specified channel.
    else:
        pass  # Handle message publish error. Check 'category' property to find out possible issue
        # because of which request did fail.
        # Request can be resent using: [status retry];


class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass  # handle incoming presence data

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass  # This event happens when radio / connectivity is lost

        elif status.category == PNStatusCategory.PNConnectedCategory:
            # Connect event. You can do stuff like publish, and know you'll get it.
            # Or just use the connected event to confirm you are subscribed for
            # UI / internal notifications, etc
            #pubnub.publish().channel('Channel-0rtj04rto').message('Alice Connected').pn_async(my_publish_callback)
            print("Bob Connected")
        elif status.category == PNStatusCategory.PNReconnectedCategory:
            pass
            # Happens as part of our regular operation. This event happens when
            # radio / connectivity is lost, then regained.
        elif status.category == PNStatusCategory.PNDecryptionErrorCategory:
            pass
            # Handle message decryption error. Probably client configured to
            # encrypt messages and on live data feed it received plain text.

    def message(self, pubnub, message):
        # Handle new message stored in message.message
        global ledger_count
        if ledger_count > 10:
            os. _exit(0)
        if 'Bob' != message.publisher:
            print("Message Recieved:\n")
            print(json.dumps(message.message, sort_keys=True, indent=4, separators=(',', ':')))
            if verify_block(json.dumps(message.message, sort_keys=True, indent=4, separators=(',', ':'))) == True:
                block = mine()
                #write to ledger? about block
                print("Sending Message:\n")
                print(json.dumps(block, sort_keys=True, indent=4, separators=(',', ':')))
                pubnub.publish().channel('Channel-0rtj04rto').message(block).pn_async(my_publish_callback)
            else:
                print("Error: block hash invalid")
        

        
#####################################################################################################################################
fw = open("ledger0.json","w+")
fw.write(tx)
fw.close()

pubnub.add_listener(MySubscribeCallback())
pubnub.subscribe().channels('Channel-0rtj04rto').execute()



