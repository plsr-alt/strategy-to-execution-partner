$response = Invoke-WebRequest -Uri 'https://chatgpt.com/share/69a85507-3104-800f-8628-0b65a1a34138' -UseBasicParsing
$html = $response.Content

if ($html -match '(?s)<script id="__NEXT_DATA__"[^>]*>(.*?)</script>') {
    $jsonStr = $Matches[1]
    $data = $jsonStr | ConvertFrom-Json
    $sr = $data.props.pageProps.serverResponse.data
    Write-Output ("Title: " + $sr.title)
    Write-Output "================================"
    foreach ($item in $sr.linear_conversation) {
        if ($item.message -and $item.message.content) {
            $role = $item.message.author.role
            $parts = $item.message.content.parts
            $text = ""
            foreach ($p in $parts) {
                if ($p -is [string]) {
                    $text += $p
                }
            }
            if ($text.Trim()) {
                Write-Output ""
                Write-Output ("[" + $role + "]")
                Write-Output $text
                Write-Output "---"
            }
        }
    }
} else {
    Write-Output "No __NEXT_DATA__ found"
    Write-Output ("Page length: " + $html.Length)
}
