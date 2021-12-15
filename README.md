# genevolweb
 Genetics & Evolution Web Tools
 
  
## Technical

### Special endpoints
Set session variable to specific value: 

```/set-session-var?var={session var}:{value}```      
eg:  
```/set-session-var?var=af_dontshowinfopopup:N```

### Settings

<code>GOOGLE_ANALYTICS_MEASUREMENT_ID</code>: If this variable is present in settings, triggers tracking in google analytics<br>
(also need to ensure <code>'common.utils.google_analytics_id'</code> is added to list of context processors in settings)
>>(eg: GOOGLE_ANALYTICS_MEASUREMENT_ID = 'G-F83XGWDX9N')

### Graph tests
```puml
A -> B
```


```plantuml
digraph Test {
A -> B
}
```
