<html>
    <head>
        <style>
                body{
                    display: flex;
                    justify-content: left;
                    align-items: top;
                    padding: 20px;
                    background: #5a7233;
                }

                table.hovertable{
                    font-family: Verdana, Arial,sans-serif;
                    font-size: 17px;
                    color: #333333;
                    border-width: 1px;
                    border-color: #999999;
                    border-collapse: collapse;
                }
                table.hovertable th{
                    background-color: #ff0000;
                    border-width: 1px;
                    padding: 8px;
                    border-style: solid;
                    border-color: #a9c6c9;
                }
                table.hovertable tr{
                    background-color: #d4e3e5;
                }
                table.hovertable td{
                    border-width: 1px;
                    padding: 8px;
                    border-style: solid;
                    border-color: #a9c6c9;
                }
        </style>
    <head>
    <body>
        <table class="hovertable">
        % include('row', values=headers, header=True)
        % for row in rows:
            % include('row', values=row, header=False)
        % end
        </table>
    </body>
</html>
