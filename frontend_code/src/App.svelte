<script>
	import Dropzone from "svelte-file-dropzone";

	let accepted = []
	let url = ""
	$: name = ""
	$: best_display = false
	$: default_url = ""
	let poke_image
	$: display_url = ''
	$: ready = false

	async function get_classification(){
		await new Promise(r => setTimeout(r, 15));
		best_display = false
		const res = await fetch("https://main-pokemon-classifier-imjeffhi4.endpoint.ainize.ai/classify/", {
			method: "POST",
			body: JSON.stringify({poke_image}),
		})
		const json = await res.json()
		name = json['Name']
		display_url = json["Display"]
		best_display = display_url ? true : false
		default_url = json['Default']
		ready = true
	}


function displayImage(){
	ready =false
	if (accepted.length > 0){
		let image = accepted[0]
		let reader = new FileReader()
		reader.readAsDataURL(image)
		reader.onload =  e => {
			const test = e.target.result
			poke_image = test
		}
	}
	else if (url){
		poke_image = url
	}
	get_classification()
  }

  function reset(){
	url = ""
	poke_image = ""
	ready = false
  }
  function handleInput(){
	let image = new Image();
	image.onload = function() {
		if (this.width > 0) {
			displayImage()
		}
	}
	image.onerror = function() {
		reset()
		alert("The entered URL is not a valid Image URL. Please try again.")
	}
	image.src = url
}
  function handleFilesSelect(e) {
    const { acceptedFiles, fileRejections } = e.detail;
	if( fileRejections.length !== 0||(acceptedFiles.length>=1&&acceptedFiles[0].name.includes('.svg'))){
		console.log(fileRejections)
		reset()
		alert("The selected file is not in an accepted format. Please only include .png, .jpg, jpeg, or .gif files.")
	}
	else{
		accepted = [...acceptedFiles]
		displayImage()
	}
  }
</script>

<div class='app-container'>
	<nav>
		<h1>Pokemon Classifier</h1>
	</nav>
	<main>
		<p>Upload an image or copy and paste an Image URL to call the Vision Transformer and predict the name of the Pokemon.</p>
		<div class="main-container">
			<article class="input card">
				<div class='dropzone'>
					<Dropzone on:drop={handleFilesSelect} multiple={false} accept="image/*" />
				</div>
				<p class="or">or</p>
				<input placeholder="Paste image URL here" type="text" class='url' bind:value={url} on:change={handleInput}>
				{#if poke_image}
					<div>
						<img id="input_image" src="{poke_image}" alt="Input"  width="224" height="224"/>
					</div>
				{/if}
			</article>
			<article class="output card">
				{#if ready}
					<div class="contents">
						<h2>It's {name}!</h2>
						{#if best_display}
							<img src={display_url} alt="Output Pokemon" width="224" height="224">
						{:else}
							<img src={default_url} alt="Output Pokemon" width="224" height="224">
						{/if}
					</div>
				{/if}
			</article>
		</div>
		<div class='disclaimer'>
			<p>All images of Pokemon displayed to the right are sprites owned by <a href="https://www.nintendo.com/">Nintendo</a>.</p>
		</div>
	</main>	
</div>
<style>
	.disclaimer{
		text-align: center;
		font-size: 9px;
	}
	.dropzone{
		width: 90%;
		margin: auto;
	}
	.dropzone:hover{
		cursor: pointer;
	}
	.url{
		width: 75%;
		text-align: center;
	}
	#input_image{
		padding: 10px;
		margin: auto;
	}
	.contents{
		margin:auto;
		text-align: center;
	}
	.input{
		margin: auto;
		text-align: center;
	}
	.or{
		text-align: center;
		padding: 0px;
		margin: 10px 0px;
	}
	.card{
		border: white 1px solid;
		flex-grow:1; 
		min-width:45%;
		min-height: 400px;
		padding: 10px;
		margin: 1px 5px;
	}
	.main-container{
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
	}
	.app-container{
		width: 85%;
		margin: auto;
	}
	nav{
		background-color: rgb(217, 19, 17, 255);
		padding:10px;
		margin-top:0px;
		border-radius:2px;
		color: rgb(255, 203, 7);
	}
	h1{
		text-shadow: 1px 1px 1px rgb(56, 107, 178);
		font-family: Helvetica, Sans-Serif;
		font-size: 32px;
		font-weight: bold;
	}
	h2{
		color: white;
		font-family: Helvetica, Sans-Serif;
	}
</style>