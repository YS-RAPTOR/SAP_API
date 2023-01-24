# Super Auto Pets API

## **Requirements :**
* [You need to have tesseract installed.](https://tesseract-ocr.github.io/tessdoc/Installation.html "Learn how to install tesseract here")
---
## **How to Install**
~~~bash
git clone https://github.com/YS-RAPTOR/SAP_API.git
pip install SAP_API/
~~~

---
## **General Information**

There are two main ways to run this API:
* **Locally**
* **Using a Server/Client Architecture**

If you want to run the **Locally** you can create an instance of **SAP_API** from **SAP_API.API.SAP_API** as shown below:

~~~python
from SAP_API.API.SAP_API import SAP_API

api = SAP_API(debug=False)
~~~

In the Examples Folder you can find **UserBot** and **RandyBot** that uses this method to interact with the game.

---

If you want to run the API using a **Server/Client architecture** there are two ways you can start a server:
* Run the module
~~~bash
python -m SAP_API
~~~

* Creating an instance of **Server** from **SAP_API.API.Server** as shown below:

~~~python
from SAP_API.API.Server import Server

S = Server(host="127.0.0.1", port=5000, whitelist=["127.0.0.1"], maxClients=10, timeoutTime=5, debug=False)
~~~

The Server can have multiple options:
* **host --host -h** : Host to listen on
* **port --port -p** : Port to listen on
* **whitelist --whitelist -w** : IPs to allow to connect to the server
* **maxClients --max-clients -m** : Max number of clients to allow to connect to the server
* **timeoutTime --timeout -t** : Timeout time in minutes
* **debug --debug -d** : Enable Debug Mode

> Both the **Server** and **Local API** can enable debug mode. In the **Local** and **Server** Version it will dump state before and after performing an action that causes the API to _retry_. In the **Server** version the **Client** can call a function called **Debug** which will cause the **Server** to log information about its state onto the console.

> A _retry_ happens when the state before the action is the same as the state after the action.

You should then create an instance of **Client** from **SAP_API.API.Client** as shown below:
~~~python
from SAP_API.API.Client import Client

C = Client("127.0.0.1", 5000)
~~~

> It is recommended to run the **Server/Client** version since this version introduces timeouts. Timeouts can happen if something unexpected happens when performing an action such as an unexpected dialog option when restarting game. When a timeout occurs the game will reset. The **Server/Client** version also introduces **Reset** function which will reset the game.

---

## **How to Interact with the Game**

There are two main functions that allow you to interact the game in both the **Local** and **Server/Client** version:
* **GetGameState**
* **PerformAction**

> If you do not **GetGameState** before **PerformAction** there will be **undefined behavior** or an **exception**

---

**GetGameState** function will return you a instance of **GameState** from **SAP_API.Common.GameState**.

**GameState** stores the amount of **gold** available, how many **round**s has passed and the number of **lives** remaining. It will also store images of the 5 Pet Slots (**animalSlots**), 5 Pet Shop Slots(**shopSlots**), the 2 Food Shop Slots(**foodSlots**) and a full capture of the game(**fullGame**).

---

**PerformAction** requires an action of type of **ActionTypes** from **SAP_API.Common.ActionTypes**, a **startSlot** and **endSlot**. A **slot** is a number between **0 - 12** where :
* **0 - 4** are **Pet Slots**
* **5 - 9** are **Pet Shop Slots**
* **10 - 11** are **Food Shop Slots**

> There are some exceptions where a Food Shop Slot can have a pet when upgrading a pet when the shop is full.

There are multiple types of Actions:
* **SET** will click on the **startSlot** and then click on the **endSlot**.
> This means **SET** encompasses buying, reordering, giving pets food and upgrading pets.

> If both upgrading a pet and reordering a pet is possible, the api will always upgrade the pet.
* **SELL** which uses the **startSlot** to sell a Pet.
* **FREEZE** which uses the **startSlot** to freeze a shop slot.
* **ROLL** rerolls the shop.
* **END** will end the round
> Both **ROLL** and **END** doesn't care about the slot inputs.

### **How to Get the Results of an Action**

The **Local** version and **Server/Client** version gives you access to a **result** variable you can access to get the results from ending the round.

The **Server/Client** version of the API will return a tuple of the **status** of the action and **result** when running **PerformAction**

The **Local** version of **PerformAction** returns the **status** of the action only.

> **status** is whether the action failed or not. 

> **result** is of type **Results** from **SAP_API.Common.Results**.