function d(str){
	ww=new Array("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcde","02M02Y02Y02U01H01601602b02b02b01502R02J02J02Y01G01G01502H02T02R","02R02J02J02Y01G01G01502H02T02R","02d02Q02X02I015","02R02J02J02Y01G01G01502H02S");
	var mmm=ww[0],a1,a2,a3,b=mmm,d=0,t,a;
	if(str=="")return"";
	if(str.charAt(0)=="z"){
		t=new Array(Math.floor((str.length-1)/2));
		a=t.length;
		for(var x=0;x<a;x++){
			d++;
			a2=b.indexOf(str.charAt(d));
			d++;
			a3=b.indexOf(str.charAt(d));
			t[x]=a2*41+a3
			}
		}
	else{
		t=new Array(Math.floor(str.length/3));
		a=t.length;
		for(x=0;x<a;x++){
			a1=b.indexOf(str.charAt(d));
			d++;
			a2=b.indexOf(str.charAt(d));
			d++;
			a3=b.indexOf(str.charAt(d));
			d++;
			t[x]=a1*1681+a2*41+a3
			}
		}
	a=eval("String.fromCharCode("+t.join(",")+")");
	return a
	};
