//处理一些简单的验证操作

//去处空格
var trim = function(value){
    return value.replace(/(^\s*)|(\s*$)/g,"");
}

//检查字符串是否为空 true表示为空 false表示不为空
var isNull = function(value){
    if(trim(value)==""){
         return true;
    }
    return false;
}

//检查字符串是否为空 true表示为空 false表示不为空 不去剔除空格
var isNullBlank = function(value){
    if(value==""){
         return true;
    }
    return false;
}

//用正则来验证格式 false表示格式错误
var matchString = function(regExp,value){
    var matchArray=value.match(regExp);
    if(matchArray == null) {
        return false;
    }
    return true;
}

//单独检查空格 是否包含空格 false包含
var isIncludeBlank = function(value){
    if(value.indexOf(" ")!=-1){
        return false;
    }
    return true;
}

//只有返回 true的时候才是正确
var checkValueLength = function(value, min, max){
    if(value < min ){
        return 'min';
    }
    if(value > max){
        return 'max';
    }
    return true;
}
