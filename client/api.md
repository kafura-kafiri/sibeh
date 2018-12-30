# SnappGo Api v0.1
###### _this version is beta and have to test it in real world before deploying_
## all url paths start with /v0.1

### Accounting
#### we can have new user key in this hang
- url


    /{hang}/{user}
- Method:
    
    PUT
- Url Params:

    None
- Data Params:
    
    key=[String]
- Success Response
    - Code 200, Content: Key
    
- Sample Call:
    
    
    $.ajax({
        url: '/food/malmal',
        type: "PUT",
        data: {key: "secret key"}
        success: function(r): {
            console.log(r)
        }
    });

#### we can change privilege of this new user key in this hang
##### user with privilege of x can't make users with privilege of y which y >= x
- url


    /{hang}/{user}@privilege={privilege}
- Method:
    
    POST
- Url Params:

    None
- Data Params:
    
    key=[String]
- Success Response
    - Code 200, Content: Key
    
- Sample Call:
    
    
    $.ajax({
        url: '/food/malmal@privilege=o',
        type: "POST",
        data: {key: "secret key"}
        success: function(r): {
            console.log(r)
        }
    });

#### add credit for this hang
- url


    /{hang}/{user_id}@credit={credit}
- Method:
    
    POST
- Url Params:

    None
- Data Params:
    
    key=[String]
- Success Response
    - Code 200, Content: Key
    
- Sample Call:
    
    
    $.ajax({
        url: '/food/mehrad@credit=1000',
        type: "POST",
        data: {key: "secret key"}
        success: function(r): {
            console.log(r)
        }
    });


#### we have to add shift for porter activation
- url


    /{hang}/{user_id}@shifts={head_h}:{head_m}:{head_s};{tail_h}:{tail_m}:{tail_s}
- Method:
    
    POST
- Url Params:

    None
- Data Params:
    
    key=[String]
    fcm=[String]
    capacity=[Int]
- Success Response
    - Code 200, Content: Key
    
- Sample Call:
    
    
    $.ajax({
        url: '/food/malmal@shifts=3:14:0;6:28:0',
        type: "POST",
        data: {
            key: "secret key",
            fcm: "fcm token",
            capacity: 20,
        },
        success: function(r): {
            console.log(r)
        }
    });
requests.post(host + ''.format(
        head.hour, head.minute, head.second,
        tail.hour, tail.minute, tail.second,
    ), data={'key': ps[0], 'fcm': 'masoud'})


### Graph QL
#### we can query to mongodb directly, and get result like birds in the sky
#### boss key required
- url


    /{hang}/!!/{collection}
- Method:
    
    POST | DELETE | PUT | PATCH
- Url Params:

    None
- Data Params:
    
    key=[String]
    q=[Json]
- Success Response
    - Code 200, Content: Key
    
- Sample Call:
    
    
    $.ajax({
        url: '/food/!!/credits',
        type: "POST",
        data: {
            key: "secret key",
            q: '{}',
        },
        success: function(r): {
            console.log(r)
        }
    });


### Oracle


### Solver
#### this endpoint will match based of specific algorithm then send a notification to each matched free porter
##### just bossed can do that
- url


   /{hang}/!!!/{algorithm}'
- Method:
    
    POST
- Url Params:

    None
- Data Params:
    
    key=[String]
- Success Response
    - Code 200, Content: Key
    
    
- Algorithm supported right now

    - rnd: random match
    - grd: brute force greedy minimum available free porter
    - hng: hungarian optimization
        
- Sample Call:
    
    
    $.ajax({
        url: '/food/!!!/hng'',
        type: "POST",
        data: {
            key: "secret key",
        },
        success: function(r): {
            console.log(r)
        }
    });

### Routing

### Motion
#### each porter can send his location
- url


    /{hang}/{user_id}@{lat},{lng} 
- Method:
    
    POST | PUT
- Url Params:

    None
- Data Params:
    
    key=[String]
- Success Response
    - Code 200, Content: {}
    - Code 201, Content: {}
    
- Sample Call:
    
    
    $.ajax({
        url: '/food/malmal@31,52',
        type: "POST",
        data: {key: "secret key"}
        success: function(r): {
            console.log(r)
        }
    });
    
    
#### we can observe one path's location
- url


    /food/~{path}@
- Method:
    
    GET
- Url Params:

    key=[String]
- Data Params:
    
    None
- Success Response
    - Code 200, Content: {lat: 31, lng: 53, date: "std datetime"}
    
- Sample Call:
    
    
    $.ajax({
        url: '/food/~P0001@',
        type: "GET",
        data: {key: "secret key"}
        success: function(r): {
            console.log(r)
        }
    });
    
#### we can observe one porters's location + it's paths
- url


    /food/{user_id}@
- Method:
    
    GET
- Url Params:

    key=[String]
- Data Params:
    
    None
- Success Response
    - Code 200, Content: {lat: 31, lng: 53, date: "std datetime"}
    - Code 200, Content: {lat: 31, lng: 53, date: "std datetime", *[points of deliveries]}
    
- Sample Call:
    
    
    $.ajax({
        url: '/food/malmal@',
        type: "GET",
        data: {key: "secret key"}
        success: function(r): {
            console.log(r)
        }
    });
    
### Scenario
#### we can sometimes insert a path
- url


    /food/~{s_lat},{s_lng};{t_lat},{t_lng}
- Method:
    
    POST | PUT
- Url Params:

    None
- Data Params:
    
    key=[String],
    transmitter=[Json],
    receiver=[Json]
    
    - Optional:
        volume=[Int],
        priority=[Int],
        delay=[Int],
    
- Success Response
    - Code 200, Content: {}
    
- Sample Call:
    
    
    $.ajax({
        url: '/food/~31,53;32,54',
        type: "POST",
        data: {
            key: "secret key",
            volume: 2,
            priority: 1,
            delay: 
        }
        success: function(r): {
            console.log(r)
        }
    });

#### call this endpoint and all porters from db goes to ram
#### just boss can do
- url


    /food
- Method:
    
    PATCH
- Url Params:

    None
- Data Params:
    
    key=[String]
- Success Response
    - Code 200, Content: {}
    
- Sample Call:
    
    
    $.ajax({
        url: '/food',
        type: "PATCH",
        data: {key: "secret key"}
        success: function(r): {
            console.log(r)
        }
    });


#### when a porter call this endpoint it means he receive fcm notification. and accept the path
- url


    /{hang}/~{path_id}@ack
- Method:
    
    PATCH
- Url Params:

    None
- Data Params:
    
    key=[String]
- Success Response
    - Code 200, Content: {}
    
- Sample Call:
    
    
    $.ajax({
        url: '/food/~P0001@ack',
        type: "POST",
        data: {key: "secret key"}
        success: function(r): {
            console.log(r)
        }
    });


#### call this endpoint and all porters from db goes to ram
#### just boss can do
- url


    /{hang}/~{path_id}@done
- Method:
    
    PATCH
- Url Params:

    None
- Data Params:
    
    key=[String]
- Success Response
    - Code 200, Content: {}
    
- Sample Call:
    
    
    $.ajax({
        url: '/food/~P0001@done',
        type: "POST",
        data: {key: "secret key"}
        success: function(r): {
            console.log(r)
        }
    });

**working on:** **_patching_**, _nack penalty_, _express radius_, _finance_
[visit!](gooz.com)