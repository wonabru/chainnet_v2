<!-- wp:paragraph -->
<p><em>At present, a law that is still in existence derived from Roman law, resulting from the desire to subjugate others (hierarchical system = FIAT money):</em></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph {"fontSize":"medium"} -->
<p class="has-medium-font-size"><em>Qui tacet consentire videtur -&nbsp;</em><strong><em>Silence is considered a sign of consent</em></strong><em>.</em></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><em>And the </em><strong><em>natural law</em></strong><em> that contradicts it, which is basically a default law </em><strong><em>for every human</em></strong><em> (I sign all my limbs under the following statement):</em></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph {"fontSize":"medium"} -->
<p class="has-medium-font-size"><strong><em>The lack of my action / decision is the lack of my acceptance, i.e. silence means no consent.</em></strong></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><em>For confirmation, I can quote about its naturalness high-tech solutions that implement this principle, namely: the value implemented in any known software compiler:</em></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><em>The default parameter value is FALSE, 0, ... etc.</em></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph -->
<p><strong><em>This is the main drive of appearing Chainnet</em></strong></p>
<!-- /wp:paragraph -->

<!-- wp:paragraph {"align":"center","fontSize":"medium"} -->
<p style="text-align:center" class="has-medium-font-size"><em>The main idea of <strong>C</strong></em><strong><em>hainnet</em></strong><em> is to build blockchain that needs recipient to sign the block in order to get money.</em></p>
<!-- /wp:paragraph -->

<!-- wp:list -->
<ul><li>No need of 51% consensus of network to accept block, thus instant transactions.</li>
    <li>The true possibility and space of implementing Post-Quantum Cryptography, which because of speed and large sizes of private and public keys impossible to implement in currently used blockchain schemes.</li><li>Negative transactions fees, what can be understood as negative friction. Activity in network builds its value and supply, so stabilize its price.</li><li>No infant time of this blockchain. Chainnet is secure from very beginning.</li><li>Joining to network is per invitation, so someone who is in the network can create new accounts, so closely related to real human social network.</li><li>No need to store whole blockchain on each node, so no proxy servers which operate on your name. Everybody can operate Chainnet from smartphone. Idea of true decentralization.</li><li>Problem of blockchains’ oracle is solved in Chainnet, by introducing temporary Oracle (some endpoint on internet) on which each participant of a transaction agreed. Because it is not permanent Oracle, but defined temporary by users of each transaction, it is also fully secure. The Oracle possibility makes Chainnet as the secure hedge for spot transaction among different blockchains (cross-blockchains DEX). In this sense Chainnet can be defined as meta-blockchain.</ul>
<!-- /wp:list -->

Storage structure in Chainnet:

https://drive.google.com/file/d/1qL9Unblo03oR6xyeT8zejbxUNybYsXiz/view?usp=sharing

Architecture scheme:

https://drive.google.com/file/d/14Qkt-kVUtlySzOfkKslWz9xz6_iL7YEb/view?usp=sharing

Flow Chart (sending coins):

https://drive.google.com/file/d/174RJsX8Ep9iL93IPkKBpp0GB1uuEisIl/view?usp=sharing

Possible solution of Cross-blockchains DEX by means of Chainnet:

https://www.draw.io/?lightbox=1&highlight=0000ff&edit=_blank&layers=1&nav=1&page-id=WnRQjQuZmzYBiC_cBbqv&title=Chainnet_Flow_SEND_TOKENS.drawio#Uhttps%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D174RJsX8Ep9iL93IPkKBpp0GB1uuEisIl%26export%3Ddownload

How to run prototype:
    
     git clone https://github.com/wonabru/chainnet_v2.git
     cd chainnet
     mkdir DB
     mkdir wallets_cipher
     python chainnet_run.py
