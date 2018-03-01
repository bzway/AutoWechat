window.onload = function () {
    $("#msgHelp").children().on("click", function () {
        var item = $(this);
        $("#txtMsg").insertContent("{" + item.text().trim() + "}");
    });
};

function LoadFriends(datas) {
    $("#loadPanel").html("");
    var temp = $(".user-item");
    for (var i = 0; i < datas.length; i++) {
        var item = temp.clone();
        item.data("id", datas[i].UserName);
        item.attr("title", loadData(datas[i]));
        item.text((datas[i].RemarkName == "" ? datas[i].NickName : datas[i].RemarkName));
        $("#loadPanel").append(item);
    }
}


function loadData(data) {

    var reg = new RegExp("'|\"", "g")
    var temp = {
        "NickName": data.NickName.replace(reg, "’"),
        "RemarkName": data.RemarkName,
        "Sex": data.Sex == 0 ? "未知" : data.Sex == 1 ? "男" : "女",
        "Signature": data.Signature.replace(reg, "’"),
        "PYInitial": data.PYInitial + "|" + data.PYQuanPin + "|" + data.RemarkPYInitial + "|" + data.RemarkPYQuanPin,
        "Province": data.Province,
        "City": data.City,
        "DisplayName": data.DisplayName
    }
    return JSON.stringify(temp, null, 4); // Indented with tab

}
function SelectUser(sender) {
    if ($(sender).parent().attr("id") == "sendPanel") {
        $("#loadPanel").append($(sender));
    } else {
        $("#sendPanel").append($(sender));
    }
    var count = $('#sendPanel').children().length;
    if (count > 0) {
        $('#txtCount').text('发送消息（已经选择' + count + '人）');
    } else {
        $('#txtCount').text('发送消息');
    }
}
function SendMsg() {
    var msg = $("#txtMsg").val();
    var to = $('#sendPanel').children();
    var len = to.length;
    var sleeptime = Math.random() * (len > 40 ? 5 : 0);

    for (var i = 0; i < len; i++) {
        var item = $(to[i]);
        host.sleep(sleeptime);
        try {
            var data = JSON.parse(item.attr("title"));
            host.sendMsg(msg.temp(data), item.data("id"));
            item.click();
        } catch (e) {
            alert(item.attr("title"));
            alert(e);
        }
    }
}
var isSearch = false;
function search() {
    if (isSearch) {
        return
    }
    isSearch = true;
    $('#loadPanel').children().show();
    var text = $("#txtSearch").val();
    if (text.length > 0) {
        $('#loadPanel').children().each(function (i, item) {
            //if ($(item).attr("title").indexOf(text) < 0) {
            //    $(item).hide();
            //}
            if ($(item).attr("title").isLike(text) == false) {
                $(item).hide();
            }
        });
    }
    isSearch = false;
}


String.prototype.temp = function (data) {
    var template = this;
    return template.replace(/\{([\w\.]*)\}/g, function (str, key) {
        var keys = key.split("."), v = data[keys.shift()];
        for (var i = 0, l = keys.length; i < l; i++) v = v[keys[i]];
        return (typeof v !== "undefined" && v !== null) ? v : "";
    });

};
/**
 * 为字符串添加模糊比较的方法
 * @param exp 模糊查询字符串，支持正则表达式
 * @param i 是否区分大小写
 * @returns
 */
String.prototype.isLike = function (exp, i) {
    var str = this;
    i = i == null ? false : i;
    if (exp.constructor == String) {
        /* 首先将表达式中的‘_’替换成‘.’，但是‘[_]’表示对‘_’的转义，所以做特殊处理 */
        var s = exp.replace(/_/g, function (m, i) {
            if (i == 0 || i == exp.length - 1) {
                return ".";
            } else {
                if (exp.charAt(i - 1) == "[" && exp.charAt(i + 1) == "]") {
                    return m;
                }
                return ".";
            }
        });
        /* 将表达式中的‘%’替换成‘.’，但是‘[%]’表示对‘%’的转义，所以做特殊处理 */
        s = s.replace(/%/g, function (m, i) {
            if (i == 0 || i == s.length - 1) {
                return ".*";
            } else {
                if (s.charAt(i - 1) == "[" && s.charAt(i + 1) == "]") {
                    return m;
                }
                return ".*";
            }
        });

        /*将表达式中的‘[_]’、‘[%]’分别替换为‘_’、‘%’*/
        s = s.replace(/\[_\]/g, "_").replace(/\[%\]/g, "%");

        /*对表达式处理完后构造一个新的正则表达式，用以判断当前字符串是否和给定的表达式相似*/
        var regex = new RegExp("" + s, i ? "" : "i");
        return regex.test(this);
    }
    return false;
};


//
//使用方法
//$(文本域选择器).insertContent("插入的内容");
//$(文本域选择器).insertContent("插入的内容"，数值); //根据数值选中插入文本内容两边的边界, 数值: 0是表示插入文字全部选择，-1表示插入文字两边各少选中一个字符。
//
//在光标位置插入内容, 并选中
(function ($) {
    $.fn.extend({
        insertContent: function (myValue, t) {
            var $t = $(this)[0];
            if (document.selection) { //ie
                this.focus();
                var sel = document.selection.createRange();
                sel.text = myValue;
                this.focus();
                sel.moveStart('character', -l);
                var wee = sel.text.length;
                if (arguments.length == 2) {
                    var l = $t.value.length;
                    sel.moveEnd("character", wee + t);
                    t <= 0 ? sel.moveStart("character", wee - 2 * t - myValue.length) : sel.moveStart("character", wee - t - myValue.length);

                    sel.select();
                }
            } else if ($t.selectionStart || $t.selectionStart == '0') {
                var startPos = $t.selectionStart;
                var endPos = $t.selectionEnd;
                var scrollTop = $t.scrollTop;
                $t.value = $t.value.substring(0, startPos) + myValue + $t.value.substring(endPos, $t.value.length);
                this.focus();
                $t.selectionStart = startPos + myValue.length;
                $t.selectionEnd = startPos + myValue.length;
                $t.scrollTop = scrollTop;
                if (arguments.length == 2) {
                    $t.setSelectionRange(startPos - t, $t.selectionEnd + t);
                    this.focus();
                }
            }
            else {
                this.value += myValue;
                this.focus();
            }
        }
    })
})(jQuery);