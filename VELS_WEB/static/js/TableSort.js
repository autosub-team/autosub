( function() {
var JB_Table=function(tab) {
 var up = String.fromCharCode(160,9650);
 var down = String.fromCharCode(160,9660);
// var up = String.fromCharCode(160,8593);
// var down = String.fromCharCode(160,8595);
 var no = String.fromCharCode(160,160,160,160);
 var dieses=this;
 var defsort=0;
 var startsort=-1;
 var Init_Sort=function(nr) {
  t.style.cursor="pointer";
  t.onclick = function() { dieses.sort(nr); }
  t.appendChild(document.createTextNode(no));
  t.title='Sort Table by "'+t.firstChild.data+'"';
  if(t.className.indexOf("vorsortiert-")>-1) {
   t.lastChild.data=down;
   ssort=nr;
  }
  else if(t.className.indexOf("vorsortiert")>-1) {
   t.lastChild.data=up;
   ssort=nr;
  }
  if(t.className.indexOf("sortiere")>-1) startsort=nr;
 } // Init_Sort
 var VglFkt_s=function(a,b) {
  var as=a[ssort], bs=b[ssort];
  var ret=(as>bs)?1:(as<bs)?-1:0;
  if(!ret && ssort!=defsort) {
   if (stype[defsort]=="s") { as=a[defsort]; bs=b[defsort]; ret=(as>bs)?1:(as<bs)?-1:0; }
   else ret=parseFloat(a[defsort])-parseFloat(b[defsort])
  }
  return ret;
 }
 var VglFkt_n=function(a,b) {
  var ret=parseFloat(a[ssort])-parseFloat(b[ssort]);
  if(!ret && ssort!=defsort) {
   if (stype[defsort]=="s") { var as=a[defsort],bs=b[defsort]; ret=(as>bs)?1:(as<bs)?-1:0; }
   else ret=parseFloat(a[defsort])-parseFloat(b[defsort])
  }
  return ret;
 }
 var convert=function(val,s) {
  var dmy;
  var trmdat = function() {
   if(dmy[0]<10) dmy[0] = "0"+dmy[0];
   if(dmy[1]<10) dmy[1] = "0"+dmy[1];
   if(dmy[2]<10) dmy[2] = "200"+dmy[2];
   else if(dmy[2]<20) dmy[2] = "20"+dmy[2];
   else if(dmy[2]<99) dmy[2] = "19"+dmy[2];
   else if(dmy[2]>9999) dmy[2] = "9999";
  }
  if(!isNaN(val) && val.search(/[0-9]/)!=-1) return val;
  var n = val.replace(",",".");
  if(!isNaN(n) && n.search(/[0-9]/)!=-1) return n;
  n = n.replace(/\s|&nbsp;|&#160;|\u00A0/g,"");
  if(!isNaN(n) && n.search(/[0-9]/)!=-1) return n;
  if(!val.search(/^\s*\d+\s*\.\s*\d+\s*\.\s*\d+\s+\d+:\d\d\s*$/)) {
   var dp = val.search(":");
   dmy = val.substring(0,dp-2).split(".");
   dmy[3] = val.substring(dp-2,dp);
   dmy[4] = val.substring(dp+1,dp+3);
   for(var i=0;i<5;i++) dmy[i] = parseInt(dmy[i],10);
   trmdat();
   if(dmy[3]<10) dmy[3] = "0"+dmy[3];
   if(dmy[4]<10) dmy[4] = "0"+dmy[4];
   return (""+dmy[2]+dmy[1]+dmy[0]+"."+dmy[3]+dmy[4]).replace(/ /g,"");
  }
  if(!val.search(/^\s*\d+\s*\.\s*\d+\s*\.\s*\d+/)) {
   dmy = val.split(".");
   for(var i=0;i<3;i++) dmy[i] = parseInt(dmy[i],10);
   trmdat();
   return (""+dmy[2]+dmy[1]+dmy[0]).replace(/ /g,"");
  }
  if(!val.search(/^\s*\d+:\d\d\s*$/)) {
   dmy = val.split(":");
   for(var i=0;i<2;i++) dmy[i] = parseInt(dmy[i],10);
   if(dmy[0]<10) dmy[0] = "0"+dmy[0];
   if(dmy[1]<10) dmy[1] = "0"+dmy[1];
   return (""+dmy[0]+dmy[1]).replace(/ /g,"");
  }
  stype[s]="s";
  return val.toLowerCase().replace(/\u00e4/g,"ae").replace(/\u00f6/g,"oe").replace(/\u00fc/g,"ue").replace(/\u00df/g,"ss");
 } // convert
 this.sort=function(sp) {
  if (first) {
   for(var z=0;z<nzeilen;z++) {
    var zelle=tz[z].getElementsByTagName("td"); // cells;
    Arr[z]=new Array(nspalten+1);
    Arr[z][nspalten]=tz[z];
    for(var s=0;s<nspalten;s++) {
     if (zelle[s].getAttribute("sort_key")) var zi=convert(zelle[s].getAttribute("sort_key"),s);
     else                                   var zi=convert(JB_elementText(zelle[s]),s);
     Arr[z][s]=zi ;
//         zelle[s].innerHTML += "<br>"+zi;
    }
   }
   first=0;
  }
  if(sp==ssort) {
   Arr.reverse() ;
   if ( Titel[ssort].lastChild.data==down )
    Titel[ssort].lastChild.data=up;
   else
    Titel[ssort].lastChild.data=down;
  }
  else {
   if ( ssort>=0 && ssort<nspalten ) Titel[ssort].lastChild.data=no;
   ssort=sp;
   if(stype[ssort]=="s") Arr.sort(VglFkt_s);
   else                  Arr.sort(VglFkt_n);
   Titel[ssort].lastChild.data=up;
  }
  for(var z=0;z<nzeilen;z++)
   tbdy.appendChild(Arr[z][nspalten]);
 } // sort
 var first=1;
 var ssort;
 var tbdy=tab.getElementsByTagName("tbody")[0];
 var tz=tbdy.rows;
 var nzeilen=tz.length;
 if (nzeilen==0) return;
 var nspalten=tz[0].cells.length;
 var Titel=tab.getElementsByTagName("thead")[0].getElementsByTagName("tr")[0].getElementsByTagName("th");
 var Arr=new Array(nzeilen);
 var ct=0;
 var stype=new Array(nspalten); for(var i=0;i<nspalten;i++) stype[i]="n";
 //if(!tab.title.length) tab.title="Ein Klick auf die Spalten\u00fcberschrift sortiert die Tabelle.";
 for(var i=Titel.length-1;i>-1;i--) {
  var t=Titel[i];
  if(t.className.indexOf("sortier")>-1) {
   ct++;
   Init_Sort(i);
   defsort = i ;
  }
 }
 if(ct==0) {
  for(var i=0;i<Titel.length;i++) {
   var t=Titel[i];
   Init_Sort(i);
  }
  defsort = 0;
 }
 if(startsort>=0) this.sort(startsort);
} // JB_Table
var JB_addEvent=function(oTarget, sType, fpDest) {
 var oOldEvent = oTarget[sType];
 if (typeof oOldEvent != "function") {
  oTarget[sType] = fpDest;
  } else {
   oTarget[sType] = function(e) {
   oOldEvent(e);
   fpDest(e);
  }
 }
}
var JB_getElementsByClass_TagName=function(tagname,classname) {
 var tag=document.getElementsByTagName(tagname);
 var Elements=new Array();
 for(var i=0;i<tag.length;i++) {
  if(tag[i].className.indexOf(classname)>-1) Elements[Elements.length]=tag[i];
 }
 return Elements;
}
var JB_elementText = function(elem) {
 var eT = function(ele) {
  var uele=ele.firstChild;
  while(uele) {
   if(uele.hasChildNodes()) eT(uele);
   if(uele.nodeType == 1) Text += " ";
   else if(uele.nodeType == 3) Text += uele.data;
   uele = uele.nextSibling;
  }
 }
 var Text="";
 eT(elem);
 return Text.replace(/\s+/g," ");
}
JB_addEvent(window,"onload",function(e) {
 if (!document.getElementsByTagName) return;
 if (!document.getElementsByTagName('body')[0].appendChild) return;
 var Sort_Table=JB_getElementsByClass_TagName("table","sortierbar");
 for(var i=0;i<Sort_Table.length;i++) new JB_Table(Sort_Table[i]);
});
})();
