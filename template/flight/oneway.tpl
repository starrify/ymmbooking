Oneway flight~<br>
<div id="flights">
%if flights:
%   for item in flights:
<div><strong>{{item['fn']}}</strong> : {{item}}</div>
%   end
%end
</div>
end of oneway flight~<br>
