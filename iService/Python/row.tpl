<tr onmouseover="this.style.backgroundColor = '#ffff66';" onmouseout="this.style.backgroundColor='#d4e3e5';">
% for value in values:
	% if header:
		<th>{{value}}</th>
	% else:
		<td>{{value}}</td>
	% end
% end
</tr>
